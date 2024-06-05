import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.graph_objects import Layout

from MRAG.utilities import po2slice1vs1


def plot_1vs1(grid1vs1, value1vs1, attacker, defender, plot_name):
    #TODO: Hanyang: not finished yet
    xA_s, yA_s, xD_s, yD_s = po2slice1vs1(attacker, defender, value1vs1.shape[0])
    # fixed the defender 
    dims_plot = [0, 1]
    dim1, dim2 = dims_plot[0], dims_plot[1]
    complex_x = complex(0, grid1vs1.pts_each_dim[dim1])
    complex_y = complex(0, grid1vs1.pts_each_dim[dim2])
    mg_X, mg_Y = np.mgrid[grid1vs1.min[dim1]:grid1vs1.max[dim1]: complex_x, grid1vs1.min[dim2]:grid1vs1.max[dim2]: complex_y]
    x_attackers = attacker[0][0]
    y_attackers = attacker[0][1]
    x_defenders = defender[0][0]
    y_defenders = defender[0][1]
    print("Plotting beautiful 2D plots. Please wait\n")
    fig = go.Figure(data=go.Contour(
        x=mg_X.flatten(),
        y=mg_Y.flatten(),
        z=value1vs1.flatten(),
        zmin=0.0,
        ncontours=1,
        contours_coloring = 'none', # former: lines 
        name= "Zero-Level", # zero level
        line_width = 1.5,
        line_color = 'magenta',
        zmax=0.0,
    ), layout=Layout(plot_bgcolor='rgba(0,0,0,0)')) #,paper_bgcolor='rgba(0,0,0,0)'
    # plot target set
    fig.add_shape(type='rect', x0=0.6, y0=0.1, x1=0.8, y1=0.3, line=dict(color='purple', width=3.0), name="Target")
    fig.add_trace(go.Scatter(x=[0.6, 0.8], y=[0.1, 0.1], mode='lines', name='Target', line=dict(color='purple')))
    # plot obstacles
    fig.add_shape(type='rect', x0=-0.1, y0=0.3, x1=0.1, y1=0.6, line=dict(color='black', width=3.0))
    fig.add_shape(type='rect', x0=-0.1, y0=-1.0, x1=0.1, y1=-0.3, line=dict(color='black', width=3.0))
    fig.add_trace(go.Scatter(x=[-0.1, 0.1], y=[0.3, 0.3], mode='lines', name='Obstacle', line=dict(color='black')))
    # plot the attacker
    fig.add_trace(go.Scatter(x=x_attackers, y=y_attackers, mode="markers", name='Attacker', marker=dict(symbol="triangle-up", size=10, color='red')))
    # plot the defender
    fig.add_trace(go.Scatter(x=x_defenders, y=y_defenders, mode="markers", name='Fixed Defender', marker=dict(symbol="square", size=10, color='green')))
   
    # figure settings
    fig.update_layout(title={'text': f"<b>{plot_name}<b>", 'y':0.82, 'x':0.4, 'xanchor': 'center','yanchor': 'top', 'font_size': 30})
    fig.update_layout(autosize=False, width=580, height=500, margin=dict(l=50, r=50, b=100, t=100, pad=0), paper_bgcolor="White", xaxis_range=[-1, 1], yaxis_range=[-1, 1], font=dict(size=20)) # $\mathcal{R} \mathcal{A}_{\infty}^{21}$
    fig.update_xaxes(showline = True, linecolor = 'black', linewidth = 2.0, griddash = 'dot', zeroline=False, gridcolor = 'Lightgrey', mirror=True, ticks='outside') # showgrid=False
    fig.update_yaxes(showline = True, linecolor = 'black', linewidth = 2.0, griddash = 'dot', zeroline=False, gridcolor = 'Lightgrey', mirror=True, ticks='outside') # showgrid=False,
    fig.show()
    print("Please check the plot on your browser.")
    

def animation(attackers_traj, defenders_traj, attackers_status):
    # Determine the number of steps
    num_steps = len(attackers_traj)
    num_attackers = attackers_traj[0].shape[0]
    num_defenders = defenders_traj[0].shape[0]

    # Create frames for animation
    frames = []
    for step in range(num_steps):
        attackers = attackers_traj[step]
        defenders = defenders_traj[step]
        status = attackers_status[step]

        x_list = []
        y_list = []
        symbol_list = []
        color_list = []

        # Go through list defenders
        for j in range(num_defenders):
            x_list.append(defenders[j][0])
            y_list.append(defenders[j][1])
            symbol_list += ["square"]
            color_list += ["blue"]
        
        # Go through list of attackers
        for i in range(num_attackers):
            x_list.append(attackers[i][0])
            y_list.append(attackers[i][1])
            if status[i] == -1:  # attacker is captured
                symbol_list += ["cross-open"]
            elif status[i] == 1:  # attacker has arrived
                symbol_list += ["circle"]
            else:  # attacker is free
                symbol_list += ["triangle-up"]
            color_list += ["red"]

        # Generate a frame based on the characteristic of each agent
        frames.append(go.Frame(data=go.Scatter(x=x_list, y=y_list, mode="markers", name="Agents trajectory",
                                               marker=dict(symbol=symbol_list, size=5, color=color_list), showlegend=False)))

    
    # Static object - obstacles, goal region, grid
    fig = go.Figure(data = go.Scatter(x=[0.6, 0.8], y=[0.1, 0.1], mode='lines', name='Target', line=dict(color='purple')),
                    layout=Layout(plot_bgcolor='rgba(0,0,0,0)', updatemenus=[dict(type="buttons",
                                                                            buttons=[dict(label="Play", method="animate",
                                                                            args=[None, {"frame": {"duration": 30, "redraw": True},
                                                                            "fromcurrent": True, "transition": {"duration": 0}}])])]), frames=frames) # for the legend

    # plot target
    fig.add_shape(type='rect', x0=0.6, y0=0.1, x1=0.8, y1=0.3, line=dict(color='purple', width=3.0), name="Target")
    # plot obstacles
    fig.add_shape(type='rect', x0=-0.1, y0=0.3, x1=0.1, y1=0.6, line=dict(color='black', width=3.0), name="Obstacle")
    fig.add_shape(type='rect', x0=-0.1, y0=-1.0, x1=0.1, y1=-0.3, line=dict(color='black', width=3.0))
    fig.add_trace(go.Scatter(x=[-0.1, 0.1], y=[0.3, 0.3], mode='lines', name='Obstacle', line=dict(color='black')))

    # figure settings
    # fig.update_layout(showlegend=False)  # to display the legends or not
    fig.update_layout(autosize=False, width=560, height=500, margin=dict(l=50, r=50, b=100, t=100, pad=0),
                      title={'text': "<b>Our method, t={}s<b>".format(num_steps/200), 'y':0.85, 'x':0.4, 'xanchor': 'center','yanchor': 'top', 'font_size': 20}, paper_bgcolor="White", xaxis_range=[-1, 1], yaxis_range=[-1, 1], font=dict(size=20)) # LightSteelBlue
    fig.update_xaxes(showline = True, linecolor = 'black', linewidth = 2.0, griddash = 'dot', zeroline=False, gridcolor = 'Lightgrey', mirror=True, ticks='outside') # showgrid=False
    fig.update_yaxes(showline = True, linecolor = 'black', linewidth = 2.0, griddash = 'dot', zeroline=False, gridcolor = 'Lightgrey', mirror=True, ticks='outside') # showgrid=False,
    fig.show()



def plot_scene(attackers_traj, defenders_traj, attackers_status, step, save=False, save_path='MRAG'):
    """Plot the scene of the game at a specific step.

    Args:
        attackers_traj (list): List of attackers' trajectories.
        defenders_traj (list): List of defenders' trajectories.
        attackers_status (list): List of attackers' status.
        step (int): The step to plot.
        save (bool): Whether to save the plot.
        save_path (str): The path to save the plot.
    
    Returns:
        None
    """
    assert step <= len(attackers_traj), "The step should be less than the length of the attackers' trajectories."
    attackers = attackers_traj[step]
    defenders = defenders_traj[step]
    status = attackers_status[step]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Set map boundaries
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_aspect('equal', adjustable='box')

    # Add caption
    # plt.text(0, 1.05, "Our Method", ha='center', va='center', fontsize=16)

    # Draw outer map boundary
    outer_map = plt.Rectangle((-1, -1), 2, 2, edgecolor='black', facecolor='none', linewidth=2.0)
    ax.add_patch(outer_map)

    # Draw obstacles
    obstacle1 = plt.Rectangle((-0.1, -1.0), 0.2, 0.7, edgecolor='black', facecolor='none', label='Obstacle', linewidth=2.0)
    obstacle2 = plt.Rectangle((-0.1, 0.3), 0.2, 0.3, edgecolor='black', facecolor='none', linewidth=2.0)
    ax.add_patch(obstacle1)
    ax.add_patch(obstacle2)

    # Draw target
    target = plt.Rectangle((0.6, 0.1), 0.2, 0.2, edgecolor='purple', facecolor='none', label='Target', linewidth=2.0)
    ax.add_patch(target)
    
    # Plot attackers
    for i in range(len(attackers)):
        if status[i] == 0:
            ax.plot(attackers[i, 0], attackers[i, 1], 'r^', label='Free Attacker' if i == 0 else "")
        elif status[i] == -1:
            ax.plot(attackers[i, 0], attackers[i, 1], marker=(4, 2, 0), color='red', markersize=10, label='Captured Attacker' if i == 0 else "")
        elif status[i] == 1:
            ax.plot(attackers[i, 0], attackers[i, 1], 'ro', label='Arrived Attacker' if i == 0 else "")
    
    # Plot defenders
    for i in range(len(defenders)):
        ax.plot(defenders[i, 0], defenders[i, 1], 'bs', label='Defender' if i == 0 else "")
    
    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', bbox_to_anchor=(1.05, 1))

    # Adjust the plot to ensure the legend is fully visible
    plt.tight_layout()

    if not save:
        plt.show()
    else:
        plt.savefig(f"{save_path}/scene_{step}.png", bbox_inches='tight')
        print(f"Plot saved at {save_path}.")



