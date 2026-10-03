import simpy

SIM_TIME = 100000   # seconds
BUFFER_SIZE = 5     # units each buffer can hold

stations = [
    ("Filling", 6.5),
    ("Capping", 5),
    ("Labeling", 8),
    ("Sealing", 5),
    ("Carton", 6),
]

env = simpy.Environment()

# One buffer between each pair of stations (4 buffers for 5 stations)
buffers = [simpy.Store(env, capacity=BUFFER_SIZE) for _ in range(4)]

# Seconds each station spends in each state
busy = {name: 0 for name, _ in stations}
blocked = {name: 0 for name, _ in stations}
starved = {name: 0 for name, _ in stations}
flow_times = []   # time each finished unit spent in the line


def station(i):
    name, process_time = stations[i]
    in_buffer = buffers[i - 1] if i > 0 else None
    out_buffer = buffers[i] if i < 4 else None

    while True:
        # 1. Get a unit
        if in_buffer is None:
            unit = env.now                      # Filling: new unit, stamped with its start time
        else:
            wait_start = env.now
            unit = yield in_buffer.get()        # waits here if the buffer is empty
            starved[name] += env.now - wait_start

        # 2. Process it
        yield env.timeout(process_time)
        busy[name] += process_time

        # 3. Pass it on
        if out_buffer is not None:
            wait_start = env.now
            yield out_buffer.put(unit)          # waits here if the next buffer is full
            blocked[name] += env.now - wait_start
        else:
            flow_times.append(env.now - unit)   # last station: the unit is finished


for i in range(5):
    env.process(station(i))

env.run(until=SIM_TIME)

# ---------- Results ----------
finished = len(flow_times)
print("Units finished:", finished)
print("Throughput (units/hour):", round(finished / SIM_TIME * 3600, 1))

if finished > 0:
    print("Average flow time (s):", round(sum(flow_times) / finished, 1))
else:
    print("Average flow time: no unit finished")

print()
print("station     busy%  blocked%  starved%  total%")
for name, _ in stations:
    b = busy[name] / SIM_TIME * 100
    bl = blocked[name] / SIM_TIME * 100
    st = starved[name] / SIM_TIME * 100
    print(f"{name:<10} {b:6.1f} {bl:9.1f} {st:9.1f} {b + bl + st:8.1f}")