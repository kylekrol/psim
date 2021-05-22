from psim import Configuration, Simulation
from psim.sims import AttitudeEstimatorTestGnc

import lin
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


matplotlib.rc('font', **{'size': 14})

trigger_eclipse = False
steps = 5000
#steps = int(3.5*3600/0.17)

configs = ['sensors/base', 'truth/base', 'truth/detumble']
configs = ['config/parameters/' + config + '.txt' for config in configs]
config = Configuration(configs)

config['truth.leader.attitude.w'] = lin.Vector3([-0.077216, 0.094684, 0.0952384])
config['sensors.leader.sun_sensors.model_eclipse'] = True

sim = Simulation(AttitudeEstimatorTestGnc, config)

fields = {
    'truth.t.s',
    'fc.leader.attitude.q.body_eci.error.degrees',
    'fc.leader.attitude.p.body_eci.error', 'fc.leader.attitude.p.body_eci.sigma',
    'fc.leader.attitude.w.bias.error', 'fc.leader.attitude.w.bias.sigma',
}
logs = {field: list() for field in fields}

def log():
    for field in fields:
        value = sim[field]
        if type(value) in {lin.Vector2, lin.Vector3, lin.Vector4}:
            logs[field].append(np.array(value))
        else:
            logs[field].append(value)


while not sim['fc.leader.attitude.is_valid']:
    sim.step()

if trigger_eclipse:
    for _ in range(250):
        log()
        sim.step()
    sim['sensors.leader.sun_sensors.disabled'] = True
    for _ in range(steps // 2):
        log()
        sim.step()
else:
    for _ in range(steps - 250):
        log()
        sim.step()
log()

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

ylim = 0.17 if trigger_eclipse else 0.03

fig = plt.figure()

ax = fig.add_subplot(311)
estimate(
    ax, logs['truth.t.s'],
    logs['fc.leader.attitude.p.body_eci.error'][:,0], logs['fc.leader.attitude.p.body_eci.sigma'][:,0],
    ylim=ylim, grid='major'
)

ax = fig.add_subplot(312)
estimate(
    ax, logs['truth.t.s'],
    logs['fc.leader.attitude.p.body_eci.error'][:,1], logs['fc.leader.attitude.p.body_eci.sigma'][:,1],
    ylabel='$p_z$, $p_y$, and $p_x$ error', ylim=ylim, grid='major'
)

ax = fig.add_subplot(313)
estimate(
    ax, logs['truth.t.s'],
    logs['fc.leader.attitude.p.body_eci.error'][:,2], logs['fc.leader.attitude.p.body_eci.sigma'][:,2],
    xlabel='$t$ (s)', ylim=ylim, grid='major'
)

fig.tight_layout()
fig.show()

fig = plt.figure()

ax = fig.add_subplot(311)
estimate(
    ax, logs['truth.t.s'],
    logs['fc.leader.attitude.w.bias.error'][:,0], logs['fc.leader.attitude.w.bias.sigma'][:,0],
    ylim=0.005, grid='major'
)

ax = fig.add_subplot(312)
estimate(
    ax, logs['truth.t.s'],
    logs['fc.leader.attitude.w.bias.error'][:,1], logs['fc.leader.attitude.w.bias.sigma'][:,1],
    ylabel='$\\beta_z$, $\\beta_y$, and $\\beta_x$ error  (rad/s)', ylim=0.005, grid='major'
)

ax = fig.add_subplot(313)
estimate(
    ax, logs['truth.t.s'],
    logs['fc.leader.attitude.w.bias.error'][:,2], logs['fc.leader.attitude.w.bias.sigma'][:,2],
    xlabel='$t$ (s)', ylim=0.005, grid='major'
)

fig.tight_layout()
fig.show()

fig = plt.figure()
plt.plot(logs['truth.t.s'], logs['fc.leader.attitude.q.body_eci.error.degrees'])
plt.yscale("log")
plt.xlabel('$t$ (s)')
plt.ylabel('Error (degrees)')
plt.grid('major')
fig.tight_layout()
fig.show()
