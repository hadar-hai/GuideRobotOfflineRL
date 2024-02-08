import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.animation import FuncAnimation
import copy


    
state = {'human_pos': [5,5], 'human_direction': np.pi /3,
            'robot_pos': [15,15], 'robot_direction': 0,
            'obstacles_pos': [[50,50,10,10],[70,70,15,15]],
            'start': [80,30], 'goal': [90,90]}       

states = []
states.append(state)
for _ in range(10):
    state  = copy.deepcopy(state)
    state['human_pos'][0] += 1
    state['human_pos'][1] += 1
    state['human_direction'] += np.pi/18
    state['robot_pos'][0] +=3
    state['robot_pos'][1] +=3
    state['robot_direction'] += np.pi/36
    states.append(state)


fig = plt.figure()
fig.set_dpi(100)
fig.set_size_inches(7, 6.5)

ax = plt.axes(xlim=(0, 100), ylim=(0, 100))
ax.set_xlim([0,100])
ax.set_ylim([0,100])
ax.set_aspect(1)

def init():
    # initialize an empty list of cirlces
    return []


def animate(i):
    state = states[i]
    patches_lst = []
    #robot pos
    patches_lst.append(ax.add_patch(patches.Circle(xy=(state['robot_pos'][0], state['robot_pos'][1]),
                                                    radius=4, linewidth=1, edgecolor='black', facecolor='blue')))
    #robot direction
    patches_lst.append(ax.add_patch(patches.Arrow(x=state['robot_pos'][0],y= state['robot_pos'][1],
                                                   dx = 10*np.cos(state['human_direction']), dy= 10*np.sin(state['human_direction']),
                                                     width=3, edgecolor='black', facecolor='royalblue')))
    # # human pos
    patches_lst.append(ax.add_patch(patches.Circle(xy=(state['human_pos'][0], state['human_pos'][1]), radius=5, linewidth=1, 
                                      edgecolor='black', facecolor='royalblue')))
    # # human direction
    patches_lst.append(ax.add_patch(patches.Arrow(x=state['human_pos'][0], y=state['human_pos'][1], dx = 10*np.cos(state['human_direction']),
                   dy= 10*np.sin(state['human_direction']), width=3, edgecolor='black', facecolor='royalblue')))
    # tether
    line, = ax.plot([state['human_pos'][0],state['robot_pos'][0]],
                                [state['human_pos'][1],state['robot_pos'][1]], c='black')
    patches_lst.append(line)
    # start
    patches_lst.append(ax.add_patch(patches.Circle(xy=(state['start'][0], state['start'][1]),
                                                    radius=5, linewidth=1, edgecolor='black', facecolor='yellow')))
    # goal
    patches_lst.append(ax.add_patch(patches.Circle(xy=(state['goal'][0], state['goal'][1]),
                                                           radius=5, linewidth=1, edgecolor='black', facecolor='green')))
    # obstacles
    for pos in state['obstacles_pos']:
        obstacle = patches.Rectangle(xy=(pos[0], pos[1]), width=pos[2], height=pos[3], linewidth=1, edgecolor='black', facecolor='r')
        patches_lst.append(ax.add_patch(obstacle))

    return  patches_lst




anim = FuncAnimation(fig, animate, init_func=init,
                               frames=len(states), interval=100, blit=True,
                               repeat=False)

plt.show()


        