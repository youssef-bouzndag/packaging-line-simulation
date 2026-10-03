import pandas as pd
from openpyxl.chart import BarChart, LineChart, Reference
from line_model import simulate, stations

BUFFER_SIZE = 5
SEEDS = [1, 2, 3, 4, 5]
TIE_MARGIN = 1   # stations within this many points of the top count as tied bottlenecks

# ---------- 1. Average of 5 runs ----------
runs = [simulate(BUFFER_SIZE, seed) for seed in SEEDS]

# ---------- 2. How each station spends its time ----------
rows = []
for name, process_time in stations:
    row = {"station": name, "process_time_s": process_time}
    for state in ["busy", "down", "blocked", "starved"]:
        row[state + "_%"] = round(sum(r[name][state] for r in runs) / len(runs), 1)
    row["working_%"] = round(row["busy_%"] + row["down_%"], 1)   # processing or being repaired
    rows.append(row)
stations_df = pd.DataFrame(rows)

# ---------- 3. Bottleneck(s) = the station(s) that work the most ----------
top = stations_df["working_%"].max()
close = stations_df[stations_df["working_%"] >= top - TIE_MARGIN]["station"].tolist()
bottleneck = " / ".join(close)
stations_df["bottleneck"] = stations_df["station"].apply(
    lambda s: "YES" if s in close else ""
)

# Stations that are slowest on paper (same process time)
slowest_time = stations_df["process_time_s"].max()
slowest = stations_df[stations_df["process_time_s"] == slowest_time]["station"].tolist()

# ---------- 4. Line KPIs ----------
kpis = pd.DataFrame([
    {"metric": "Buffer size", "value": BUFFER_SIZE},
    {"metric": "Runs averaged", "value": len(runs)},
    {"metric": "Throughput (units/hour)",
     "value": round(sum(r["throughput"] for r in runs) / len(runs), 1)},
    {"metric": "Average flow time (s)",
     "value": round(sum(r["flow_time"] for r in runs) / len(runs), 1)},
    {"metric": "Bottleneck(s), measured", "value": bottleneck},
    {"metric": "Number of stations tied", "value": len(close)},
    {"metric": "Slowest on paper (same process time)", "value": " / ".join(slowest)},
])

# ---------- 5. Buffer size study ----------
study = []
for size in [1, 2, 5, 10, 20]:
    rs = [simulate(size, seed) for seed in SEEDS]
    study.append({
        "buffer_size": size,
        "throughput_per_h": round(sum(r["throughput"] for r in rs) / len(rs), 1),
        "flow_time_s": round(sum(r["flow_time"] for r in rs) / len(rs), 1),
    })
study_df = pd.DataFrame(study)

# ---------- 6. Excel report with big charts ----------
with pd.ExcelWriter("packaging_report.xlsx", engine="openpyxl") as writer:
    kpis.to_excel(writer, sheet_name="KPIs", index=False)
    stations_df.to_excel(writer, sheet_name="Stations", index=False)
    study_df.to_excel(writer, sheet_name="Buffer study", index=False)

    for ws in writer.sheets.values():
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = 36

    # Chart 1: how each station spends its time (stacked bars)
    ws = writer.sheets["Stations"]
    n = len(stations_df)
    chart = BarChart()
    chart.type = "col"
    chart.grouping = "stacked"
    chart.overlap = 100
    chart.title = f"Station time use (buffer {BUFFER_SIZE}) - bottleneck: {bottleneck}"
    chart.y_axis.title = "% of time"
    # columns C to F = busy_%, down_%, blocked_%, starved_%
    chart.add_data(Reference(ws, min_col=3, max_col=6, min_row=1, max_row=n + 1),
                   titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=2, max_row=n + 1))
    for series, color in zip(chart.series, ["2563EB", "DC2626", "F59E0B", "9CA3AF"]):
        series.graphicalProperties.solidFill = color
    chart.x_axis.tickLblPos = "low"
    chart.x_axis.delete = False
    chart.y_axis.delete = False
    # reserve room for the titles so they do not sit on the numbers
    chart.title.overlay = False
    chart.legend.overlay = False
    chart.y_axis.title.overlay = False
    chart.width, chart.height = 30, 16
    ws.add_chart(chart, "J2")

    # Charts 2 and 3: buffer size vs throughput, and vs flow time
    ws = writer.sheets["Buffer study"]
    m = len(study_df)
    for col, title, axis_title, cell in [
        (2, "Throughput by buffer size", "Units per hour", "F2"),
        (3, "Flow time by buffer size", "Seconds", "F32"),
    ]:
        c = LineChart()
        c.title = title
        c.x_axis.title = "Buffer size (units)"
        c.y_axis.title = axis_title
        c.add_data(Reference(ws, min_col=col, min_row=1, max_row=m + 1), titles_from_data=True)
        c.set_categories(Reference(ws, min_col=1, min_row=2, max_row=m + 1))
        c.x_axis.tickLblPos = "low"
        c.x_axis.delete = False
        c.y_axis.delete = False
        # reserve room for the titles so they do not sit on the numbers
        c.title.overlay = False
        c.x_axis.title.overlay = False
        c.y_axis.title.overlay = False
        c.width, c.height = 26, 14
        ws.add_chart(c, cell)

print(kpis.to_string(index=False))
print()
print(stations_df.to_string(index=False))
print()
print(study_df.to_string(index=False))
print("\nSaved packaging_report.xlsx (charts are inside the file)")