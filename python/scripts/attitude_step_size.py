from psim import Configuration, Simulation
from psim.sims import SingleAttitudeOrbitGnc

import lin
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


matplotlib.rc('font', **{'size': 14})

factor = 2
steps = 5000 * factor

configs = ['sensors/base', 'truth/base', 'truth/deployment']
configs = ['config/parameters/' + config + '.txt' for config in configs]
config = Configuration(configs)

config['truth.dt.ns'] = config['truth.dt.ns'] // factor

sim = Simulation(SingleAttitudeOrbitGnc, config)

fields = {
    'truth.t.s',
    'truth.leader.attitude.q.body_eci.norm', 'truth.leader.attitude.L.norm',
}
logs = {field: list() for field in fields}

def log():
    for field in fields:
        value = sim[field]
        if type(value) in {lin.Vector2, lin.Vector3, lin.Vector4}:
            logs[field].append(np.array(value))
        else:
            logs[field].append(value)


for _ in range(steps):
    log()
    sim.step()

for field in fields:
    logs[field] = np.array(logs[field])
logs['truth.t.s'] = logs['truth.t.s'] - logs['truth.t.s'][0]


fig = plt.figure()

plt.plot(logs['truth.t.s'], logs['truth.leader.attitude.q.body_eci.norm'])
plt.xlabel('$t$ (s)')
plt.ylabel('Quaternion Norm')

fig.tight_layout()
fig.show()

fig = plt.figure()

plt.plot(logs['truth.t.s'], logs['truth.leader.attitude.L.norm'])
plt.xlabel('$t$ (s)')
plt.ylabel('$H$ (kg m$^2$/s)')

fig.tight_layout()
plt.show()
