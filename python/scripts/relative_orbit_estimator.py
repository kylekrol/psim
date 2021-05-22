from psim import Configuration, Simulation
from psim.sims import RelativeOrbitEstimatorTest

import lin
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


matplotlib.rc('font', **{'size': 14})

steps = 5000

configs = ['sensors/base', 'truth/base', 'truth/deployment']
configs = ['config/parameters/' + config + '.txt' for config in configs]
config = Configuration(configs)

sim = Simulation(RelativeOrbitEstimatorTest, config)

fields = {
    'truth.t.s',
    'fc.follower.relative_orbit.r.hill.error', 'fc.follower.relative_orbit.r.hill.sigma',
    'fc.follower.relative_orbit.v.hill.error', 'fc.follower.relative_orbit.v.hill.sigma',
    'truth.follower.orbit.E', 'truth.follower.orbit.r.eci',
}
logs = {field: list() for field in fields}

def log():
    for field in fields:
        value = sim[field]
        if type(value) in {lin.Vector2, lin.Vector3, lin.Vector4}:
            logs[field].append(np.array(value))
        else:
            logs[field].append(value)


while not sim['fc.follower.relative_orbit.is_valid']:
    sim.step()

for _ in range(steps):
    log()
    sim.step()

for field in fields:
    logs[field] = np.array(logs[field])
logs['truth.t.s'] = logs['truth.t.s'] - logs['truth.t.s'][0]


def estimate(ax, t, error, sigma, ylim=0.01, **kwargs):
    ax.plot(t, error, '-')
    ax.plot(t,  3.0 * sigma, '-.g')
    ax.plot(t, -3.0 * sigma, '-.g')
    ax.set_xlabel(kwargs.get('xlabel'))
    ax.set_ylabel(kwargs.get('ylabel'))
    ax.set_ylim(-ylim, ylim)
    ax.grid(kwargs.get('grid'))
    ax.set_axisbelow(True)

fig = plt.figure()

ax = fig.add_subplot(311)
estimate(
    ax, logs['truth.t.s'],
    logs['fc.follower.relative_orbit.r.hill.error'][:,0], logs['fc.follower.relative_orbit.r.hill.sigma'][:,0],
    grid='major', ylim=0.06
)

ax = fig.add_subplot(312)
estimate(
    ax, logs['truth.t.s'],
    logs['fc.follower.relative_orbit.r.hill.error'][:,1], logs['fc.follower.relative_orbit.r.hill.sigma'][:,1],
    grid='major', ylabel='$\delta r_z$, $\delta r_y$, and $\delta r_x$ error (m)', ylim=0.06
)

ax = fig.add_subplot(313)
estimate(
    ax, logs['truth.t.s'],
    logs['fc.follower.relative_orbit.r.hill.error'][:,2], logs['fc.follower.relative_orbit.r.hill.sigma'][:,2],
    grid='major', xlabel='$t$ (s)', ylim=0.06
)

fig.tight_layout()
fig.show()

fig = plt.figure()

ax = fig.add_subplot(311)
estimate(
    ax, logs['truth.t.s'],
    logs['fc.follower.relative_orbit.v.hill.error'][:,0], logs['fc.follower.relative_orbit.v.hill.sigma'][:,0],
    grid='major', ylim=0.004
)

ax = fig.add_subplot(312)
estimate(
    ax, logs['truth.t.s'],
    logs['fc.follower.relative_orbit.v.hill.error'][:,1], logs['fc.follower.relative_orbit.v.hill.sigma'][:,1],
    grid='major', ylabel='$\delta v_z$, $\delta v_y$, and $\delta v_x$ error (m/s)', ylim=0.004
)

ax = fig.add_subplot(313)
estimate(
    ax, logs['truth.t.s'],
    logs['fc.follower.relative_orbit.v.hill.error'][:,2], logs['fc.follower.relative_orbit.v.hill.sigma'][:,2],
    grid='major', xlabel='$t$ (s)', ylim=0.08
)

fig.tight_layout()
fig.show()
