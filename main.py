# Internal Imports
from Game import Game

# Main game loop
running = True
goal_reached = False

# Start Game
game = Game()

# Game loop
goal_reached = game.game_loop(running, goal_reached)
# quit the game when it's done
game.quit_game()
