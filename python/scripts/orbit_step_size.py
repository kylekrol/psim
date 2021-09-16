from psim import Configuration, Simulation
from psim.sims import SingleOrbitGnc

import lin
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


matplotlib.rc('font', **{'size': 14})

steps = 3600 * 500 * 8

configs = ['sensors/base', 'truth/base', 'truth/deployment']
configs = ['config/parameters/' + config + '.txt' for config in configs]
config = Configuration(configs)

sim = Simulation(SingleOrbitGnc, config)

fields = {
    'truth.t.s',
    'truth.leader.orbit.E', 'truth.leader.orbit.r.eci',
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

plt.plot(logs['truth.t.s'], logs['truth.leader.orbit.E'])
plt.xlabel('$t$ (s)')
plt.ylabel('Orbital Energy (J)')
plt.grid('major')

fig.tight_layout()
fig.show()

fig = plt.figure()

ax = fig.add_subplot(111, projection='3d')
ax.plot(logs['truth.leader.orbit.r.eci'][:,0], logs['truth.leader.orbit.r.eci'][:,1], logs['truth.leader.orbit.r.eci'][:,2])
ax.set_xlabel('$r_x$ (m)')
ax.set_ylabel('$r_y$ (m)')
ax.set_zlabel('$r_z$ (m)')

fig.tight_layout()
plt.show()
