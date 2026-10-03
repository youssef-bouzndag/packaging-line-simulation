import simpy
import random

SIM_TIME = 100000   # seconds
MTBF = 600          # average operating seconds between breakdowns
MTTR = 60           # average repair seconds
CV = 0.1            # processing time variation (10%)
SEEDS = [1, 2, 3, 4, 5]

stations = [
    ("Filling", 6.5),
    ("Capping", 5),
    ("Labeling", 8),
    ("Sealing", 5),
    ("Carton", 6),
]


def simulate(buffer_size, seed, breakdowns=True):
    rng = random.Random(seed)
    env = simpy.Environment()
    buffers = [simpy.Store(env, capacity=buffer_size) for _ in range(4)]

    busy = {name: 0 for name, _ in stations}
    down = {name: 0 for name, _ in stations}
    blocked = {name: 0 for name, _ in stations}
    starved = {name: 0 for name, _ in stations}
    flow_times = []

    def station(i):
        name, mean = stations[i]
        in_buffer = buffers[i - 1] if i > 0 else None
        out_buffer = buffers[i] if i < 4 else None
        time_to_fail = rng.expovariate(1 / MTBF)   # working seconds until the next breakdown

        while True:
            # 1. Get a unit
            if in_buffer is None:
                unit = env.now
            else:
                wait_start = env.now
                unit = yield in_buffer.get()
                starved[name] += env.now - wait_start

            # 2. Process it. A breakdown can happen in the middle of the unit
            remaining = max(0.1 * mean, rng.gauss(mean, CV * mean))
            while remaining > 0:
                if breakdowns and time_to_fail < remaining:
                    # work until the failure moment
                    yield env.timeout(time_to_fail)
                    busy[name] += time_to_fail
                    remaining -= time_to_fail
                    # repair, then carry on with the same unit
                    repair = rng.expovariate(1 / MTTR)
                    yield env.timeout(repair)
                    down[name] += repair
                    time_to_fail = rng.expovariate(1 / MTBF)
                else:
                    yield env.timeout(remaining)
                    busy[name] += remaining
                    time_to_fail -= remaining
                    remaining = 0

            # 3. Pass it on
            if out_buffer is not None:
                wait_start = env.now
                yield out_buffer.put(unit)
                blocked[name] += env.now - wait_start
            else:
                flow_times.append(env.now - unit)

    for i in range(5):
        env.process(station(i))
    env.run(until=SIM_TIME)

    finished = len(flow_times)
    return {
        "throughput": finished / SIM_TIME * 3600,
        "flow_time": sum(flow_times) / finished if finished > 0 else 0,
        "busy": busy, "down": down, "blocked": blocked, "starved": starved,
    }


def average(buffer_size, breakdowns=True):
    runs = [simulate(buffer_size, seed, breakdowns) for seed in SEEDS]
    throughput = sum(r["throughput"] for r in runs) / len(runs)
    flow_time = sum(r["flow_time"] for r in runs) / len(runs)
    return throughput, flow_time


# ---------- Part A: breakdowns off vs on (buffer 5) ----------
print("PART A: effect of breakdowns (buffer 5, average of 5 runs)")
print("scenario            throughput/h   flow time (s)")
for label, flag in [("no breakdowns", False), ("with breakdowns", True)]:
    th, ft = average(5, flag)
    print(f"{label:<18} {th:12.1f} {ft:15.1f}")

# ---------- Part B: station detail (buffer 5, seed 1) ----------
print("\nPART B: station detail (one run, seed 1)")
r = simulate(5, 1, True)
print("station     busy%  down%  blocked%  starved%  total%")
for name, _ in stations:
    b = r["busy"][name] / SIM_TIME * 100
    d = r["down"][name] / SIM_TIME * 100
    bl = r["blocked"][name] / SIM_TIME * 100
    st = r["starved"][name] / SIM_TIME * 100
    print(f"{name:<10} {b:6.1f} {d:6.1f} {bl:9.1f} {st:9.1f} {b + d + bl + st:8.1f}")

# ---------- Part C: buffer size vs throughput ----------
print("\nPART C: buffer size (breakdowns on, average of 5 runs)")
print("buffer size   throughput/h   flow time (s)")
for size in [1, 2, 5, 10, 20]:
    th, ft = average(size, True)
    print(f"{size:11d} {th:14.1f} {ft:15.1f}")