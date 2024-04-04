# Internal Imports
from Game import Game
from Agents import *

# Set agents.
player1_agent = ABehavioralCloning_LidarBased_WithGoal() # ABehavioralCloning_LidarBased_WithGoal(), 
                                                        # BehavioralCloning_LidarBased_WithGoal(), 
                                                        # BehavioralCloning_ImagesBasedAgent(), 
                                                        # GoalFollowImproved() # no obstacles avoidance
# player1_agent.lidar_based_with_goal_less_beams_flag = False
player2_agent = EpsilonLeashFollow() 
# player2_agent.epsilon = 0.5

# Data saving flag:
data_save_flag = False

# Main game loop
running = True
goal_reached = False

# Start Game
# If at least one agent is default or None, Game will assume human players (keyboard input)
game = Game(player1_agent, player2_agent, data_save_flag)
# game = Game()

# Game loop
goal_reached = game.game_loop(running, goal_reached)
# quit the game when it's done
game.quit_game()
