# Internal Imports
from Game import Game
from Agents import *

# Set agents.
player1_agent = None
player2_agent = EpsilonLeashFollow()

# Main game loop
running = True
goal_reached = False

# Start Game
# If at least one agent is default or None, Game will assume human players (keyboard input)
game = Game(player1_agent, player2_agent)
# game = Game()

# Game loop
goal_reached = game.game_loop(running, goal_reached)
# quit the game when it's done
game.quit_game()
