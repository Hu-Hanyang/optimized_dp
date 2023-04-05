import numpy as np
from utilities import *
from odp.Grid import Grid
from compute_opt_traj import compute_opt_traj1v0
from odp.solver import HJSolver, computeSpatDerivArray
from MRAG.AttackerDefender1v0 import AttackerDefender1v0
from MRAG.AttackerDefender1v1 import AttackerDefender1v1 
from odp.Plots.plotting_utilities import *
from MaximumMatching import MaxMatching


# This debug for not loading spatial derivatives array before the game
# Simulation 4 baseline: 8 attackers with 4 defenders
# preparations
print("Preparing for the simulaiton... \n")
T = 1.5 # total simulation time T = [0.130s (26 A0 by D0), 0.5s (100 A3 by D1), 0.605s (121 A7 arrived), 0.905s (181 A6 arrived), 0.990s (198 A2 by D1), 0.945s (189 A4 by D1), 1.190s (238 A5 by D0),  1.455s (291 A1 by D0)]
deltat = 0.005 # calculation time interval
times = int(T/deltat)

# load all value functions, grids and spatial derivative array
value1v0 = np.load('MRAG/1v0AttackDefend.npy')  # value1v0.shape = [100, 100, len(tau)]
# v1v1 = np.load('MRAG/1v1AttackDefend.npy')
v1v1 = np.load('MRAG/1v1AttackDefend_speed15.npy')
value1v1 = v1v1[..., np.newaxis]  # value1v1.shape = [45, 45, 45, 45, 1]
grid1v0 = Grid(np.array([-1.0, -1.0]), np.array([1.0, 1.0]), 2, np.array([100, 100])) # original 45
grid1v1 = Grid(np.array([-1.0, -1.0, -1.0, -1.0]), np.array([1.0, 1.0, 1.0, 1.0]), 4, np.array([45, 45, 45, 45])) # original 45
agents_1v0 = AttackerDefender1v0(uMode="min", dMode="max")
agents_1v1 = AttackerDefender1v1(uMode="min", dMode="max")  # 1v1 (4 dims dynamics)
tau1v0 = np.arange(start=0, stop=2.5 + 1e-5, step=0.025)
tau1v1 = np.arange(start=0, stop=4.5 + 1e-5, step=0.025)

# initialize positions of attackers and defenders
attackers_initials = [(0.5, 0.5), (-0.8, 0.8), (-0.8, 0.3), (0.0, 0.8), (-0.8, -0.2), (-0.8, -0.8), (0.8, -0.8), (0.6, -0.5)]
defenders_initials = [(0.3, 0.3), (0.3, -0.3), (-0.3, 0.3), (-0.3, -0.3)]  # [(0.3, 0.5), (-0.3, -0.5), (0.3, -0.5), (-0.3, 0.5)], [(0.3, 0.3), (-0.3, -0.3), (0.3, -0.3), (-0.3, 0.3)]


num_attacker = len(attackers_initials)
num_defender = len(defenders_initials)
attackers_trajectory  = [[] for _ in range(num_attacker)]
defenders_trajectory = [[] for _ in range(num_defender)]

# for plotting
attackers_x = [[] for _ in range(num_attacker)]
attackers_y = [[] for _ in range(num_attacker)]
defenders_x = [[] for _ in range(num_defender)]
defenders_y = [[] for _ in range(num_defender)]

# mip results
capture_decisions = []

# load the initial states
current_attackers = attackers_initials
current_defenders = defenders_initials
for i in range(num_attacker):
    attackers_trajectory[i].append(current_attackers[i])
    attackers_x[i].append(current_attackers[i][0])
    attackers_y[i].append(current_attackers[i][1])

for j in range(num_defender):
    defenders_trajectory[j].append(current_defenders[j])
    defenders_x[j].append(current_defenders[j][0])
    defenders_y[j].append(current_defenders[j][1])

# initialize the captured results
attackers_status_logs = []
attackers_status = [0 for _ in range(num_attacker)]
stops_index = []  # the list stores the indexes of attackers that has been captured
attackers_status_logs.append(attackers_status)

print("The simulation starts: \n")
# simulation starts
for _ in range(0, times):
    # print(f"The attackers in the {_} step are at {current_attackers} \n")
    # print(f"The defenders in the {_} step are at {current_defenders} \n")

    # Maximum Matching
    bigraph = bi_graph(v1v1, current_attackers, current_defenders, stops_index)
    print(f"The bigraph in the step{_} is {bigraph}. \n")
    MaxMatch = MaxMatching(bigraph)
    num, selected = MaxMatch.maximum_match()
    print(f"The maximum matching pair number is {num} \n")
    print(f"The result matching is {selected}")
    capture_decisions.append(selected)  # document the capture results

   # calculate the current controls of defenders
    control_defenders = []  # current controls of defenders, [(d1xc, d1yc), (d2xc, d2yc)]
    for j in range(num_defender):
        d1x, d1y = current_defenders[j]
        if len(selected[j]) == 1: # defender j capture the attacker selected[j][0]
            a1x, a1y = current_attackers[selected[j][0]]
            joint_states1v1 = (a1x, a1y, d1x, d1y)
            control_defenders.append(defender_control1v1_1slice(agents_1v1, grid1v1, value1v1, tau1v1, joint_states1v1))
        else:  # defender j could not capture any of attackers
            attacker_index = select_attacker2(d1x, d1y, current_attackers, stops_index)  # choose the nearest attacker
            a1x, a1y = current_attackers[attacker_index]
            joint_states1v1 = (a1x, a1y, d1x, d1y)
            control_defenders.append((0.0, 0.0))
    # print(f'The control in the {_} step of defenders are {control_defenders} \n')
    # update the next postions of defenders
    newd_positions = next_positions(current_defenders, control_defenders, deltat)  # , selected, current_captured
    current_defenders = newd_positions

    # calculate the current controls of attackers
    control_attackers = attackers_control(agents_1v0, grid1v0, value1v0, tau1v0, current_attackers)
    # print(f'The control in the {_} step of attackers are {control_attackers} \n')
    # update the next postions of attackers
    newa_positions = next_positions_a2(current_attackers, control_attackers, deltat, stops_index)
    current_attackers = newa_positions

   # document the new current positions of attackers and defenders
    for i in range(num_attacker):
        attackers_trajectory[i].append(current_attackers[i])
        attackers_x[i].append(current_attackers[i][0])
        attackers_y[i].append(current_attackers[i][1])

    for j in range(num_defender):
        defenders_trajectory[j].append(current_defenders[j])
        defenders_x[j].append(current_defenders[j][0])
        defenders_y[j].append(current_defenders[j][1])

    # check the attackers status: captured or not  
    attackers_status = capture_check(current_attackers, current_defenders, selected, attackers_status)
    attackers_status_logs.append(attackers_status)
    attackers_arrived = arrived_check(current_attackers)
    stops_index = stoped_check(attackers_status, attackers_arrived)
    print(f"The current status at iteration{_} of attackers is arrived:{attackers_arrived} + been captured:{attackers_status}. \n")

    if len(stops_index) == num_attacker:
        print(f"All attackers have arrived or been captured at the time t={(_+1)*deltat}. \n")
        break
print("The game is over. \n")

print(f"The results of the selected is {capture_decisions}. \n")
print(f"The final captured_status of all attackers is {attackers_status_logs[-1]}. \n")

# plot the trajectories seperately 
# T = [0.130s (26 A0 by D0), 0.5s (100 A3 by D1), 0.605s (121 A7 arrived), 0.905s (181 A6 arrived), 0.990s (198 A2 by D1), 0.945s (189 A4 by D1), 1.190s (238 A5 by D0),  1.455s (291 A1 by D0)]
if T == 0:  
    plot_simulation8v4_b1(attackers_x, attackers_y, defenders_x, defenders_y)
elif T == 0.1:
    plot_simulation8v4_b1s(attackers_x, attackers_y, defenders_x, defenders_y)
elif T == 0.5:
    plot_simulation8v4_b2s(attackers_x, attackers_y, defenders_x, defenders_y)
elif T == 1.0:
    plot_simulation8v4_b3s(attackers_x, attackers_y, defenders_x, defenders_y)
elif T == 1.455: # -24
    plot_simulation8v4_b2(attackers_x, attackers_y, defenders_x, defenders_y)
elif T == 1.5:
    plot_simulation8v4_b2(attackers_x, attackers_y, defenders_x, defenders_y)
else:
    plot_simulation(attackers_x, attackers_y, defenders_x, defenders_y)