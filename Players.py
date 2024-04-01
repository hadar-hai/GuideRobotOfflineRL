# This file is for the moveable players: Main_Player, Secondary_Player and Leash
# Documentation required!!!

import pygame
import math
from global_parameters import *

class Main_Player:
    def __init__(self, window, x, y, obstacles, color, player_size):
        self.window = window
        self.rect = pygame.Rect(x, y, player_size, player_size)
        self.color = color
        self.collision_flag = False
        self.reached_goal_flag = False  # Add a flag for reaching the goal
        self.player_size = player_size
        self.obstacles = obstacles

    def update_other_player(self, other_player: 'Secondary_Player' = None):
        self.other_player = other_player

    def draw(self):
        pygame.draw.circle(self.window, self.color, self.rect.center, self.player_size // 2)

    def move(self, dx, dy, font):
        new_rect = self.rect.move(dx, dy)
        player_collides_with_obstacle = any(obstacle.collides_with_circle(new_rect.centerx, new_rect.centery, PLAYER_SIZE // 2) for obstacle in self.obstacles)
        leash_collides_with_obstacle = any(obstacle.collides_with_line(new_rect.centerx, new_rect.centery, self.other_player.rect.centerx, self.other_player.rect.centery) for obstacle in self.obstacles)
        player_collides_with_wall = new_rect.centerx < 0 or new_rect.centerx > WIDTH or new_rect.centery < 0 or new_rect.centery > HEIGHT
        if player_collides_with_obstacle or leash_collides_with_obstacle or player_collides_with_wall:
            for obstacle in self.obstacles:
                if obstacle.collides_with_circle(new_rect.centerx, new_rect.centery, PLAYER_SIZE // 2):
                    if obstacle.rect.left == 800 and obstacle.rect.top == 0 and obstacle.rect.right == 1600 and obstacle.rect.bottom == 600:
                        player_collides_with_obstacle = False
        
        if not player_collides_with_obstacle and not leash_collides_with_obstacle and not player_collides_with_wall:
            self.rect = new_rect
        else:
            self.collision_flag = True
            collision_cause = ""
            if player_collides_with_obstacle:
                collision_cause = collision_cause + "robot collides with obstacle"
                for obstacle in self.obstacles:
                    if obstacle.collides_with_circle(new_rect.centerx, new_rect.centery, PLAYER_SIZE // 2):
                        print("Obstacle top: ", obstacle.rect.top, "Obstacle left: ", obstacle.rect.left, "Obstacle bottom: ", obstacle.rect.bottom, "Obstacle right: ", obstacle.rect.right)
                        print("Player: ", new_rect.centerx, new_rect.centery)
            elif leash_collides_with_obstacle:
                collision_cause = collision_cause + "leash collides with obstacle"
            elif player_collides_with_wall:
                collision_cause = collision_cause + "robot collides with wall"
            collision_text = font.render("Collision!", True, RED)
            self.window.blit(collision_text,
                        (WIDTH // 2 - collision_text.get_width() // 2, HEIGHT // 2 - collision_text.get_height() // 2))
            print("collision cause: ", collision_cause)

class Secondary_Player:
    def __init__(self, window, x, y, obstacles, color, player_size):
        self.rect = pygame.Rect(x, y, player_size, player_size)
        self.color = color
        self.collision_flag = False
        self.reached_goal_flag = False
        self.obstacles = obstacles
        self.window = window

    def update_other_player(self, other_player: 'Main_Player' = None):
        self.other_player = other_player

    def draw(self):
        pygame.draw.circle(self.window, self.color, self.rect.center, PLAYER_SIZE // 2)

    def move(self, dx, dy, font):
        new_rect = self.rect.move(dx, dy)
        player_collides_with_obstacle = any(obstacle.collides_with_circle(new_rect.centerx, new_rect.centery, PLAYER_SIZE // 2) for obstacle in self.obstacles)
        leash_collides_with_obstacle = any(obstacle.collides_with_line(new_rect.centerx, new_rect.centery, self.other_player.rect.centerx, self.other_player.rect.centery) for obstacle in self.obstacles)
        player_collides_with_wall = new_rect.centerx < 0 or new_rect.centerx > WIDTH or new_rect.centery < 0 or new_rect.centery > HEIGHT
        if player_collides_with_obstacle:
            for obstacle in self.obstacles:
                if obstacle.collides_with_circle(new_rect.centerx, new_rect.centery, PLAYER_SIZE // 2):
                    if obstacle.rect.left == 800 and obstacle.rect.top == 0 and obstacle.rect.right == 1600 and obstacle.rect.bottom == 600:
                        player_collides_with_obstacle = False
                        
        if not player_collides_with_obstacle and not leash_collides_with_obstacle and not player_collides_with_wall:      
            self.rect = new_rect
        else:
            collision_cause = ""
            if player_collides_with_obstacle:
                collision_cause = collision_cause + "human collides with obstacle"
                # find out which obstacle is colliding
                for obstacle in self.obstacles:
                    if obstacle.collides_with_circle(new_rect.centerx, new_rect.centery, PLAYER_SIZE // 2):
                        print("Obstacle top: ", obstacle.rect.top, "Obstacle left: ", obstacle.rect.left, "Obstacle bottom: ", obstacle.rect.bottom, "Obstacle right: ", obstacle.rect.right)
                        print("Player: ", new_rect.centerx, new_rect.centery)
            elif leash_collides_with_obstacle:
                collision_cause = collision_cause + "leash collides with obstacle"
            elif player_collides_with_wall:
                collision_cause = collision_cause + "human collides with wall"
            self.collision_flag = True
            collision_text = font.render("Collision! GAME OVER!", True, RED)
            self.window.blit(collision_text,
                        (WIDTH // 2 - collision_text.get_width() // 2, HEIGHT // 2 - collision_text.get_height() // 2))
            print("collision cause: ", collision_cause)


class Leash:
    def __init__(self, window, player1, player2, length):
        self.player1 = player1
        self.player2 = player2
        self.length = length
        self.window = window

    def draw(self):
        pygame.draw.line(self.window, BLUE, self.player1.rect.center, self.player2.rect.center, 2)

    def update(self):
        # Calculate distance between players
        dist = math.sqrt((self.player1.rect.centerx - self.player2.rect.centerx) ** 2 +
                         (self.player1.rect.centery - self.player2.rect.centery) ** 2)
        return dist
