import simpy
import random

MTBF = 600   # average working seconds between breakdowns
MTTR = 60    # average repair seconds
CV = 0.1     # processing time variation (10%)

stations = [
    ("Filling", 6.5),
    ("Capping", 5),
    ("Labeling", 8),
    ("Sealing", 6),
    ("Carton", 5),
]


def simulate(buffer_size, seed, sim_time=100000, breakdowns=True):
    rng = random.Random(seed)
    env = simpy.Environment()
    n = len(stations)
    buffers = [simpy.Store(env, capacity=buffer_size) for _ in range(n - 1)]

    busy = {name: 0 for name, _ in stations}
    down = {name: 0 for name, _ in stations}
    blocked = {name: 0 for name, _ in stations}
    starved = {name: 0 for name, _ in stations}
    flow_times = []

    def station(i):
        name, mean = stations[i]
        in_buffer = buffers[i - 1] if i > 0 else None
        out_buffer = buffers[i] if i < n - 1 else None
        time_to_fail = rng.expovariate(1 / MTBF)

        while True:
            # 1. Get a unit
            if in_buffer is None:
                unit = env.now
            else:
                wait_start = env.now
                unit = yield in_buffer.get()
                starved[name] += env.now - wait_start

            # 2. Process it (a breakdown can happen in the middle)
            remaining = max(0.1 * mean, rng.gauss(mean, CV * mean))
            while remaining > 0:
                if breakdowns and time_to_fail < remaining:
                    yield env.timeout(time_to_fail)
                    busy[name] += time_to_fail
                    remaining -= time_to_fail
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

    for i in range(n):
        env.process(station(i))
    env.run(until=sim_time)

    finished = len(flow_times)
    result = {
        "throughput": finished / sim_time * 3600,
        "flow_time": sum(flow_times) / finished if finished > 0 else 0,
    }
    for name, _ in stations:
        result[name] = {
            "busy": busy[name] / sim_time * 100,
            "down": down[name] / sim_time * 100,
            "blocked": blocked[name] / sim_time * 100,
            "starved": starved[name] / sim_time * 100,
        }
    return result