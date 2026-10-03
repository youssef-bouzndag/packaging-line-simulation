import line_model
from line_model import simulate, stations

SEEDS = [1, 2, 3, 4, 5]
BUFFER_SIZE = 5                                   # buffer used for the checks
slowest_name, slowest_time = max(stations, key=lambda s: s[1])
MAX_THROUGHPUT = 3600 / slowest_time              # no run can beat the slowest station
ok = True


def check(name, passed, detail=""):
    global ok
    print(("PASS  " if passed else "FAIL  ") + name + (" - " + detail if detail else ""))
    if not passed:
        ok = False


runs = [simulate(BUFFER_SIZE, seed) for seed in SEEDS]

# ---------- Check 1: time accounting ----------
# Every station is always busy, down, blocked or starved, so the four add up to ~100%
worst = 0
for r in runs:
    for name, _ in stations:
        worst = max(worst, abs(sum(r[name].values()) - 100))
check("Time adds up to 100% for every station", worst < 1,
      f"largest gap {worst:.2f} points")

# ---------- Check 2: states that cannot happen ----------
first, last = stations[0][0], stations[-1][0]
check(f"{first} (first station) is never starved",
      all(r[first]["starved"] == 0 for r in runs))
check(f"{last} (last station) is never blocked",
      all(r[last]["blocked"] == 0 for r in runs))

# ---------- Check 3: throughput cannot beat the slowest station ----------
too_fast = [r["throughput"] for r in runs if r["throughput"] > MAX_THROUGHPUT * 1.01]
check(f"Throughput never above {MAX_THROUGHPUT:.0f} units/hour (+1% margin)",
      len(too_fast) == 0)

# ---------- Check 4: no randomness, no breakdowns -> hand calculation ----------
old_cv = line_model.CV
line_model.CV = 0
clean = simulate(BUFFER_SIZE, 1, breakdowns=False)
line_model.CV = old_cv

check(f"Fixed times, no breakdowns: throughput close to {MAX_THROUGHPUT:.0f}/hour",
      MAX_THROUGHPUT * 0.99 <= clean["throughput"] <= MAX_THROUGHPUT * 1.001,
      f"got {clean['throughput']:.1f}")
busiest = max(stations, key=lambda s: clean[s[0]]["busy"])[0]
check(f"Fixed times: the slowest station ({busiest}) is busy almost 100% of the time",
      clean[busiest]["busy"] > 99, f"got {clean[busiest]['busy']:.1f}%")

# ---------- Check 5: same seed gives the same result ----------
a = simulate(BUFFER_SIZE, 3)
b = simulate(BUFFER_SIZE, 3)
check("Same seed gives identical results", a["throughput"] == b["throughput"])

# ---------- Check 6: breakdowns must lower throughput ----------
with_b = sum(r["throughput"] for r in runs) / len(runs)
no_b = sum(simulate(BUFFER_SIZE, s, breakdowns=False)["throughput"] for s in SEEDS) / len(SEEDS)
check("Breakdowns lower throughput", with_b < no_b,
      f"with {with_b:.1f}, without {no_b:.1f}")

# ---------- Check 7: repair share matches the settings ----------
# Failures only happen while working, so down / (busy + down) should be near MTTR / (MTBF + MTTR)
expected = line_model.MTTR / (line_model.MTBF + line_model.MTTR) * 100
for name, _ in stations:
    d = sum(r[name]["down"] for r in runs) / len(runs)
    bz = sum(r[name]["busy"] for r in runs) / len(runs)
    share = d / (bz + d) * 100
    check(f"{name}: repair share near {expected:.1f}%", abs(share - expected) < 1.5,
          f"got {share:.1f}%")

# ---------- Check 8: a bigger buffer should not lower throughput ----------
prev = None
for size in [1, 2, 5, 10, 20]:
    th = sum(simulate(size, s)["throughput"] for s in SEEDS) / len(SEEDS)
    if prev is not None:
        check(f"Buffer {size} not worse than the previous size", th >= prev * 0.99,
              f"{prev:.1f} -> {th:.1f}")
    prev = th

print("\nAll checks passed" if ok else "\nChecks FAILED")