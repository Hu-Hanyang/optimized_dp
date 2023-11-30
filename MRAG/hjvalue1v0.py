import numpy as np
# Utility functions to initialize the problem
from odp.Grid import Grid
from odp.Shapes import *
# Specify the  file that includes dynamic systems, AttackerDefender4D
from MRAG.AttackerDefender1v0 import AttackerDefender1v0
# Plot options
from odp.Plots import PlotOptions
from odp.Plots.plotting_utilities import plot_2d, plot_isosurface, plot_original
# Solver core
from odp.solver import HJSolver, computeSpatDerivArray
import math

""" USER INTERFACES
- Define grid
- Generate initial values for grid using shape functions
- Time length for computations
- Initialize plotting option
- Call HJSolver function
"""

##################################################### EXAMPLE 6 1v0AttackerDefender ####################################

grids = Grid(np.array([-1.0, -1.0]), np.array([1.0, 1.0]), 2, np.array([100, 100])) # original 45

# Define my object dynamics
agents_1v0 = AttackerDefender1v0(uMode="min", dMode="max")  # 1v1 (4 dims dynamics)

# Avoid set, no constraint means inf
obs1_attack = ShapeRectangle(grids, [-0.1, -1.0], [0.1, -0.3])  # attacker stuck in obs1
obs2_attack = ShapeRectangle(grids, [-0.1, 0.30], [0.1, 0.60])  # attacker stuck in obs2
# obs3_capture = agents_1v0.capture_set(grids, 0.1, "capture")  # attacker being captured by defender, try different radius
avoid_set = np.minimum(obs1_attack, obs2_attack)

# Reach set, run and see what it is!
goal1_destination = ShapeRectangle(grids, [0.6, 0.1], [0.8, 0.3])  # attacker arrives target
# goal2_escape = agents_1v0.capture_set(grids, 0.1, "escape")  # attacker escape from defender
# obs1_defend = ShapeRectangle(grids, [-1000, -1000, -0.1, -1000], [1000, 1000, 0.1, -0.3])  # defender stuck in obs1
# obs2_defend = ShapeRectangle(grids, [-1000, -1000, -0.1, 0.30], [1000, 1000, 0.1, 0.60])  # defender stuck in obs2
reach_set = goal1_destination
# plot_original(grids, reach_set)

# Look-back length and time step
lookback_length = 2.5  # the same as 2014Mo 
t_step = 0.025

# Actual calculation process, needs to add new plot function to draw a 2D figure
small_number = 1e-5
tau = np.arange(start=0, stop=lookback_length + small_number, step=t_step)

# while plotting make sure the len(slicesCut) + len(plotDims) = grid.dims
po = PlotOptions(do_plot=False, plot_type="2d_plot", plotDims=[0, 1], slicesCut=[22, 22])
# plot the 2 obs
# plot_isosurface(g, np.minimum(obs1_attack, obs2_attack), po)
# plot_isosurface(g, obs3_capture, po)

# In this example, we compute a Reach-Avoid Tube
compMethods = {"TargetSetMode": "minVWithVTarget", "ObstacleSetMode": "maxVWithObstacle"} # original one
# compMethods = {"TargetSetMode": None}
result = HJSolver(agents_1v0, grids, [reach_set, avoid_set], tau, compMethods, po, saveAllTimeSteps=True) # original one
# result = HJSolver(agents_1v0, grids, reach_set, tau, compMethods, po, saveAllTimeSteps=True)

print(f'The shape of the value function is {result.shape} \n')
# save the value function
# np.save('/localhome/hha160/optimized_dp/MRAG/1v0AttackDefend.npy', result)
np.save('MRAG/1v0AttackDefend.npy', result)

# # compute spatial derivatives at every state
# x_derivative = computeSpatDerivArray(grids, result, deriv_dim=1, accuracy="low")
# y_derivative = computeSpatDerivArray(grids, result, deriv_dim=2, accuracy="low")

# # Let's compute optimal control at some random idices
# spat_deriv_vector = (x_derivative[10,20], y_derivative[10,20])

# # Compute the optimal control
# opt_a1, opt_a2 = agents_1v0.optCtrl_inPython(spat_deriv_vector)
# print("Optimal accel is {}\n".format(opt_a1))
# print("Optimal rotation is {}\n".format(opt_a2))