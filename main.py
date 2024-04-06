# Internal Imports
from Game import Game
from Agents import *

def evaluate_agents(player1_agent, player2_agent):
    # Data saving flag:
    data_save_flag = False
    limit_steps = True

    # Main game loop
    running = True
    goal_reached = False

    # Start Game
    # If at least one agent is default or None, Game will assume human players (keyboard input)
    game = Game(player1_agent, player2_agent, data_save_flag, limit_steps)


    # Game loop
    goal_reached = game.game_loop(running, goal_reached)
    # quit the game when it's done
    game.quit_game()

    return goal_reached

no_tests = 100

agents = [GoalFollowImproved(), BehavioralCloning_LidarBased_WithGoal(), ABehavioralCloning_LidarBased_WithGoal()]
success_counts = [0, 0, 0]

player2_agent = EpsilonLeashFollow()

for agent_id in range(len(agents)):
    player1_agent = agents[agent_id]

    for test in range(no_tests):
        success = evaluate_agents(player1_agent, player2_agent)
        if success:
            success_counts[agent_id] += 1

print(success_counts)



