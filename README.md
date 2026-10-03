# Packaging Line Simulation

A discrete-event simulation of a **5-station packaging line**, built with **Python and SimPy**.

The project identifies bottlenecks, shows how each station spends its time, and evaluates how **buffer size affects throughput and flow time**.

All data is simulated. The line is generic and could represent a **food, beverage, cosmetics, or pharmaceutical packaging line**.

---

## Contents

1. [Project Structure](#1-project-structure)
2. [How to Run](#2-how-to-run)
3. [How the Model Works](#3-how-the-model-works)
4. [Output](#4-output)
5. [Validator](#5-validator)
6. [Limitations](#6-limitations)
7. [Requirements and License](#7-requirements-and-license)

---

## 1. Project Structure

```text
packaging-line-simulation/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── 01_simulate_line.py
│   └── Lesson 1: Fixed processing times, no breakdowns
│
├── 02_random_line.py
│   └── Lesson 2: Random processing times, breakdowns, and buffer sizes
│
├── line_model.py
│   └── Reusable simulation model used by the report and validator
│
├── 03_report.py
│   └── Bottleneck detection and Excel report generation
│
└── validator.py
    └── Independent checks of the model's output
```

---

## 2. How to Run

### Step 1 — Install the requirements

```bash
pip install -r requirements.txt
```

### Step 2 — Run the basic simulation

```bash
python 01_simulate_line.py
```

This runs the simple packaging line with fixed processing times and no breakdowns.

### Step 3 — Run the random simulation

```bash
python 02_random_line.py
```

This version introduces:

* Random processing times
* Equipment breakdowns
* Different buffer sizes

### Step 4 — Generate the Excel report

```bash
python 03_report.py
```

This generates:

```text
packaging_report.xlsx
```

> **Note:** Close `packaging_report.xlsx` before running `03_report.py` again. Otherwise, Python may not be able to overwrite the file.

### Step 5 — Run the validator

```bash
python validator.py
```

The validator runs approximately **35 simulations** and checks whether the model behaves as expected.

---

## 3. How the Model Works

### Production Line

The simulated line consists of **5 stations in series**:

1. Filling
2. Capping
3. Labeling
4. Sealing
5. Carton

A buffer (waiting area) is located between each pair of stations.

The first station always has access to material, while the output of the final station leaves the production line.

### Station States

At any point during the simulation, each station can be in one of four states:

| State       | Description                                                         |
| ----------- | ------------------------------------------------------------------- |
| **Busy**    | The station is processing a unit.                                   |
| **Down**    | The station is being repaired after a breakdown.                    |
| **Blocked** | The station has finished a unit, but the downstream buffer is full. |
| **Starved** | The station is waiting because the upstream buffer is empty.        |

The simulation tracks how much time each station spends in each state.

### Randomness

Processing times vary by approximately **±10% around each station's average processing time**.

Equipment breakdowns are also simulated:

* A breakdown occurs after approximately **600 working seconds on average**.
* The average repair time is approximately **60 seconds**.
* A breakdown can occur while a unit is being processed.

---

## 4. Output

The `03_report.py` script generates an Excel workbook:

```text
packaging_report.xlsx
```

The workbook contains three sheets.

### 4.1 KPIs

This sheet reports the main performance indicators:

* Throughput
* Flow time
* Bottleneck(s)
* Number of tied bottleneck stations

### 4.2 Station States

This sheet shows the percentage of time each station spends:

* Busy
* Down
* Blocked
* Starved

It also includes a **stacked bar chart** for visual comparison.

### 4.3 Buffer Study

This sheet evaluates different buffer sizes from **1 to 20**.

It reports:

* Throughput
* Flow time

Line charts are included to show how performance changes as buffer capacity increases.

### Bottleneck Detection

If several stations have the same slowest processing time, the report identifies **all of them as tied bottlenecks** rather than arbitrarily selecting one station.

---

## 5. Validator

The `validator.py` script performs independent checks to verify that the simulation behaves correctly.

It checks the following:

1. **State percentages**
   The four station states should add up to approximately 100% of the simulation time.

2. **Boundary conditions**

   * The first station should never be starved.
   * The last station should never be blocked.

3. **Maximum theoretical throughput**
   Throughput should never exceed:

   ```text
   3600 / slowest station processing time
   ```

4. **Deterministic case**
   With no randomness and no breakdowns, the simulation should match the expected hand calculation.

5. **Reproducibility**
   Running the simulation with the same random seed should produce the same result.

6. **Breakdown impact**
   Introducing breakdowns should reduce throughput.

7. **Repair share**
   The percentage of time spent repairing should be consistent with the specified breakdown parameters.

8. **Buffer capacity**
   Increasing buffer size should not reduce throughput under the model's assumptions.

### Validation Run Length

The checks are designed for relatively long simulations, with a default duration of approximately:

```text
100,000 simulated seconds
```

Very short simulations may cause some checks to fail because of:

* Start-up effects
* End-of-simulation effects
* Too few breakdown events

These failures do not necessarily indicate a problem with the simulation model.

---

## 6. Limitations

The model uses several simplifying assumptions:

* Breakdowns occur only while a station is processing.
* A blocked or starved station cannot experience a breakdown.
* All buffers have the same capacity.
* Repairs are random and there is no preventive maintenance schedule.
* Waiting and repair activities still in progress when the simulation ends are not fully counted, so time percentages can be slightly below 100%.
* The model represents a single product.
* All production data is simulated.
* Operators are not explicitly modeled.
* Material shortages are not modeled.

---

## 7. Requirements and License

### Requirements

* **Python 3.9+**
* **SimPy**
* **Pandas**
* **OpenPyXL**

See `requirements.txt` for the exact dependencies.

### License

This project is licensed under the **MIT License**.
