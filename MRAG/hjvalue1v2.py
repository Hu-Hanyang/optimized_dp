import os
import time
import psutil
import numpy as np
# Utility functions to initialize the problem
from odp.Grid import Grid
from odp.Shapes import *
# Specify the  file that includes dynamic systems, AttackerDefender4D
from MRAG.AttackerDefender1v2 import AttackerDefender1v2 
# Plot options
from odp.Plots import PlotOptions
from odp.Plots.plotting_utilities import plot_2d, plot_isosurface
# Solver core
from odp.solver import HJSolver, computeSpatDerivArray

""" USER INTERFACES
- 1. Define grid
- 2. Instantiate the dynamics of the agent
- 3. Generate initial values for grid using shape functions
- 4. Time length for computations
- 5. Initialize plotting option
- 6. Call HJSolver function
"""

##################################################### EXAMPLE 5 1 vs. 2 AttackerDefender ####################################
# Record the time of whole process
start_time = time.time()

# 1. Define grid
grids = Grid(np.array([-1.0, -1.0, -1.0, -1.0, -1.0, -1.0]), np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
             6, np.array([30, 30, 30, 30, 30, 30]))

# First load the 4D reach-avoid set
RA_1V1 = np.load("1v1AttackDefend_g30_speed1.npy")

# 2. Instantiate the dynamics of the agent
agents_1v2 = AttackerDefender1v2(uMode="min", dMode="max")  # 1v1 (4 dims dynamics)

# 3. Avoid set, no constraint means inf
obs1_attack = ShapeRectangle(grids, [-0.1, -1.0, -1000, -1000, -1000, -1000], [0.1, -0.3, 1000, 1000, 1000, 1000])  # attacker stuck in obs1
obs1_attack = np.array(obs1_attack, dtype='float32')
obs2_attack = ShapeRectangle(grids, [-0.1, 0.30, -1000, -1000, -1000, -1000], [0.1, 0.60, 1000, 1000, 1000, 1000])  # attacker stuck in obs2
obs2_attack = np.array(obs2_attack, dtype='float32')
obs_attack = np.minimum(obs1_attack, obs2_attack)
del obs1_attack
del obs2_attack

obs3_capture1 = agents_1v2.capture_set1(grids, 0.1, "capture")  # attacker being captured by defender, try different radius
obs3_capture1 = np.array(obs3_capture1, dtype='float32')
obs3_capture2 = agents_1v2.capture_set2(grids, 0.1, "capture")  # attacker being captured by defender, try different radius
obs3_capture2 = np.array(obs3_capture2, dtype='float32')
obs3_capture = np.minimum(obs3_capture1, obs3_capture2)
del obs3_capture1
del obs3_capture2

avoid_set = np.minimum(obs3_capture, obs_attack) # original

#TODO: Not finished yet Reach set, run and see what it is!
goal1_destination = ShapeRectangle(grids, [0.6, 0.1, -1000, -1000, -1000, -1000], [0.8, 0.3, 1000, 1000, 1000, 1000])  # attacker arrives target
goal2_escape1 = agents_1v2.capture_set1(grids, 0.1, "escape")  # attacker escape from defender
goal2_escape2 = agents_1v2.capture_set2(grids, 0.1, "escape")  # attacker escape from defender
goal2_escape = np.maximum(goal2_escape1, goal2_escape2)

# Defender 1 gets stuck in obs and (xA, xD2) in RA_1V1
obs1_defend1 = ShapeRectangle(grids, [-1000, -1000, -0.1, -1000, -1000, -1000], [1000, 1000, 0.1, -0.3, 1000, 1000])  # defender 1 stuck in obs1
obs1_defend1 = np.array(obs1_defend1, dtype='float32')
obs2_defend1 = ShapeRectangle(grids, [-1000, -1000, -0.1, 0.30, -1000, -1000], [1000, 1000, 0.1, 0.60, 1000, 1000])  # defender 1 stuck in obs2
obs2_defend1 = np.array(obs2_defend1, dtype='float32')
obs_defender1 = np.minimum(obs1_defend1, obs2_defend1)
del obs1_defend1
del obs2_defend1

a_win_with_d2 = np.expand_dims(RA_1V1, axis = (2, 3))
a_win_with_d2 = np.array(a_win_with_d2, dtype='float32')

a_win_d1_obs_d2 = np.minimum(a_win_with_d2, obs_defender1)

# Defender 2 gets stuck in obs and (xA, xD1) in RA_1V1
obs1_defend2 = ShapeRectangle(grids, [-1000, -1000, -1000, -1000, -0.1, -1000], [1000, 1000, 1000, 1000, 0.1, -0.3])  # defender 2 stuck in obs1

a2_lose_after_a1 = -(np.zeros((30, 30, 30, 30, 30, 30)) + np.expand_dims(RA_1V1, axis = (0, 1)))
a2_lose_after_a1 = np.array(a2_lose_after_a1, dtype='float32')


obs1_defend2 = ShapeRectangle(grids, [-1000, -1000, -1000, -1000, -0.1, -1000], [1000, 1000, 1000, 1000, 0.1, -0.3])  # defender stuck in obs1
obs2_defend2 = ShapeRectangle(grids, [-1000, -1000, -0.1, 0.30, -0.1, 0.30], [1000, 1000, 0.1, 0.60, 0.1, 0.60])  # defender stuck in obs2

reach_set = np.minimum(np.maximum(goal1_destination, goal2_escape), np.minimum(obs1_defend, obs2_defend)) # original

# Look-back length and time step
lookback_length = 10  # the same as 2014Mo
t_step = 0.025

# Actual calculation process, needs to add new plot function to draw a 2D figure
small_number = 1e-5
tau = np.arange(start=0, stop=lookback_length + small_number, step=t_step)

# while plotting make sure the len(slicesCut) + len(plotDims) = grid.dims
po = PlotOptions(do_plot=False, plot_type="2d_plot", plotDims=[0, 1], slicesCut=[22, 22])

# In this example, we compute a Reach-Avoid Tube
compMethods = {"TargetSetMode": "minVWithVTarget", "ObstacleSetMode": "maxVWithObstacle"} # original one
# compMethods = {"TargetSetMode": "minVWithVTarget"}
solve_start_time = time.time()

result = HJSolver(agents_1v2, grids, [reach_set, avoid_set], tau, compMethods, po, saveAllTimeSteps=None) # original one
# result = HJSolver(my_2agents, g, avoid_set, tau, compMethods, po, saveAllTimeSteps=True)
process = psutil.Process(os.getpid())
print(f"The CPU memory used during the calculation of the value function is {process.memory_info().rss/(1024 ** 3): .2f} GB.")  # in bytes

solve_end_time = time.time()
print(f'The shape of the value function is {result.shape} \n')
print(f"The size of the value function is {result.nbytes / (1024 ** 3): .2f} GB or {result.nbytes/(1024 ** 2)} MB.")
print(f"The time of solving HJ is {solve_end_time - solve_start_time} seconds.")

print(f'The shape of the value function is {result.shape} \n')
# save the value function
# np.save('/localhome/hha160/optimized_dp/MRAG/1v1AttackDefend_speed15.npy', result)  # grid = 45
np.save('1v1AttackDefend_g30_speed15.npy', result)  # grid = 30
print(f"The value function has been saved successfully.")

# Record the time of whole process
end_time = time.time()
print(f"The time of whole process is {end_time - start_time} seconds.")