Packaging Line Simulation

A discrete-event simulation of a 5-station packaging line (filling, capping, labeling, sealing, carton), built step by step with Python and SimPy. It finds the bottleneck, shows how each station spends its time, and tests how buffer size affects output.

All data is simulated. The line is generic: it could be a food, drink, cosmetics, or pharmaceutical line.

The model

* 5 stations in a row, with a buffer (waiting area) between each pair.
* The first station always has material. The last station’s output leaves the line.
* A station is blocked when the buffer after it is full, and starved when the buffer before it is empty.
* Processing times are random (10% variation around each station’s average).
* Stations break down after about 600 working seconds on average and need about 60 seconds of repair. A breakdown can happen in the middle of a unit.
* Every second of a station’s time is counted as one of four states: busy, down, blocked, starved.

Files

Column 1	Column 2
File	What it does
01_simulate_line.py	Lesson 1: fixed processing times, no breakdowns
02_random_line.py	Lesson 2: random times and breakdowns, buffer size comparison
line_model.py	The reusable simulation model used by the report and the validator
03_report.py	Bottleneck detection and an Excel report with charts
validator.py	Independent checks on the model’s output


Run it

pip install -r requirements.txt
python 01_simulate_line.py
python 02_random_line.py
python 03_report.py
python validator.py

validator.py runs about 35 simulations, so it takes a little while.

Output

03_report.py writes packaging_report.xlsx:

Column 1	Column 2
Sheet	Content
KPIs	Throughput, flow time, bottleneck(s), number of tied stations
Stations	Busy, down, blocked and starved percentage per station, with a stacked bar chart
Buffer study	Throughput and flow time for buffer sizes 1 to 20, with line charts


If several stations have the same slowest process time, the report lists all of them as tied bottlenecks, instead of picking one at random.

Validator

validator.py checks things that must be true whatever the random numbers are:

* Each station’s four states add up to about 100% of the time.
* The first station is never starved, and the last is never blocked.
* Throughput never exceeds 3600 divided by the slowest station’s time.
* With no randomness and no breakdowns, the result matches the hand calculation.
* The same seed gives the same result.
* Breakdowns lower throughput, and the repair share matches the settings.
* A bigger buffer does not reduce throughput.

These checks are written for long runs (the default is 100,000 simulated seconds). Very short runs fail some of them because of start-up and end-of-run effects and too few breakdowns, not because the model is wrong.

Limitations

* Breakdowns happen only while a station is processing. A blocked or starved station cannot fail.
* Buffers have the same size everywhere, and repair times are random but have no maintenance schedule.
* Waits and repairs still in progress when the simulation stops are not counted, which is why the time totals can be slightly under 100%.
* Single product, simulated data, no operators or material shortages.

Requirements

Python 3.9+, simpy, pandas, openpyxl (see requirements.txt).

License

MIT
