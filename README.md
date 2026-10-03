PACKAGING LINE SIMULATION

A discrete-event simulation of a 5-station packaging line, built with
Python and SimPy. It finds the bottleneck, shows how each station spends
its time, and tests how buffer size affects output.

All data is simulated. The line is generic: it could be a food, drink,
cosmetics or pharmaceutical line.

CONTENTS

1. Project structure
2. How to run
3. How the model works
4. Output
5. Validator
6. Limitations
7. Requirements and license
8. PROJECT STRUCTURE

---

packaging-line-simulation/
|-- README.txt
|-- requirements.txt
|-- .gitignore
|-- 01_simulate_line.py     Lesson 1: fixed times, no breakdowns
|-- 02_random_line.py       Lesson 2: random times, breakdowns, buffer sizes
|-- line_model.py           Reusable model (used by 03 and the validator)
|-- 03_report.py            Bottleneck detection + Excel report with charts
`-- validator.py            Independent checks on the model’s output

1. HOW TO RUN


Step 1   pip install -r requirements.txt
Step 2   python 01_simulate_line.py     (simple line, prints results)
Step 3   python 02_random_line.py       (adds randomness and breakdowns)
Step 4   python 03_report.py            (writes packaging_report.xlsx)
Step 5   python validator.py            (runs about 35 simulations)

Close packaging_report.xlsx before step 4, or Python cannot save over it.

1. HOW THE MODEL WORKS


Line

* 5 stations in a row: Filling, Capping, Labeling, Sealing, Carton.
* A buffer (waiting area) sits between each pair of stations.
* The first station always has material. The last station’s output
leaves the line.

Station states (every second is counted as exactly one of these)

* Busy      processing a unit
* Down      being repaired
* Blocked finished a unit, but the buffer after it is full.
* Starved   waiting for a unit, because the buffer before it is empty

Randomness

* Processing times vary by 10% around each station’s average.
* A station breaks down after about 600 working seconds on average and
needs about 60 seconds of repair. A breakdown can happen in the
middle of a unit.
1. OUTPUT



03_report.py writes packaging_report.xlsx with three sheets:

KPIs           Throughput, flow time, bottleneck(s), number of tied
stations
Stations       Busy / down / blocked / starved % per station, with a
stacked bar chart
Buffer study   Throughput and flow time for buffer sizes 1 to 20, with
line charts

Ties: if several stations have the same slowest process time, the report
lists all of them as tied bottlenecks instead of picking one at random.

1. VALIDATOR


validator.py checks things that must be true whatever the random numbers
are:

[1] Each station’s four states add up to about 100% of the time.
[2] The first station is never starved; the last is never blocked.
[3] Throughput never exceeds 3600 / (slowest station’s time).
[4] With no randomness and no breakdowns, the result matches the hand
calculation.
[5] The same seed gives the same result.
[6] Breakdowns lower throughput.
[7] The repair share matches the breakdown settings.
[8] A bigger buffer does not reduce throughput.

Note: the checks are written for long runs (default 100,000 simulated
seconds). Very short runs fail some of them because of start-up and
end-of-run effects and too few breakdowns, not because the model is wrong.

1. LIMITATIONS



* Breakdowns happen only while a station is processing. A blocked or
starved station cannot fail.
* All buffers have the same size. Repairs are random, with no
maintenance schedule.
* Waits and repairs still running when the simulation stops are not
counted, so time totals can be slightly under 100%.
* Single product, simulated data, no operators or material shortages.
1. REQUIREMENTS AND LICENSE



Requirements   Python 3.9+, simpy, pandas, openpyxl
(see requirements.txt)
License        MIT
