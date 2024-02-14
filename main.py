import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
PLAYER_SIZE = 10
PLAYER_SPEED = 1
LEASH_MAX_LENGTH = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
FONT = pygame.font.Font(None, 36)

# Create the game window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Map Game")

# Main_Player class
class Main_Player:
    def __init__(self, x, y, color=RED):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.color = color
        
    def update_other_player(self, other_player: 'Secondary_Player' = None):
        self.other_player = other_player

    def draw(self):
        pygame.draw.circle(window, self.color, self.rect.center, PLAYER_SIZE // 2)

    def move(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        if not any(obstacle.collides_with_circle(new_rect.centerx, new_rect.centery, PLAYER_SIZE // 2) for obstacle in obstacles) and not any(obstacle.collides_with_line(new_rect.centerx, new_rect.centery, self.other_player.rect.centerx, self.other_player.rect.centery) for obstacle in obstacles):
            self.rect = new_rect
        else: 
            collision_text = FONT.render("Collision!", True, RED)
            window.blit(collision_text, (WIDTH // 2 - collision_text.get_width() // 2, HEIGHT // 2 - collision_text.get_height() // 2))

# Secondary_Player class
class Secondary_Player:
    def __init__(self, x, y, color=BLUE):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.color = color
        
    def update_other_player(self, other_player: 'Secondary_Player' = None):
        self.other_player = other_player
        
    def draw(self):
        pygame.draw.circle(window, self.color, self.rect.center, PLAYER_SIZE // 2)

    def move(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        if not any(obstacle.collides_with_circle(new_rect.centerx, new_rect.centery, PLAYER_SIZE // 2) for obstacle in obstacles) and not any(obstacle.collides_with_line(new_rect.centerx, new_rect.centery, self.other_player.rect.centerx, self.other_player.rect.centery) for obstacle in obstacles):
            self.rect = new_rect
        else: 
            collision_text = FONT.render("Collision!", True, RED)
            window.blit(collision_text, (WIDTH // 2 - collision_text.get_width() // 2, HEIGHT // 2 - collision_text.get_height() // 2))

# Leash class
class Leash:
    def __init__(self, player1, player2, length):
        self.player1 = player1
        self.player2 = player2
        self.length = length

    def draw(self):
        pygame.draw.line(window, BLUE, self.player1.rect.center, self.player2.rect.center, 2)

    def update(self):
        # Calculate distance between players
        dist = math.sqrt((self.player1.rect.centerx - self.player2.rect.centerx) ** 2 +
                         (self.player1.rect.centery - self.player2.rect.centery) ** 2)
        
        # If the distance exceeds the maximum length, move player2 towards player1
        if dist > self.length:
            angle = math.atan2(self.player1.rect.centery - self.player2.rect.centery,
                               self.player1.rect.centerx - self.player2.rect.centerx)
            dx = int(self.length * math.cos(angle))
            dy = int(self.length * math.sin(angle))
            pygame.draw.line(window, GREEN, self.player2.rect.center, self.player1.rect.center, 5)
            pygame.display.update()  # Update display to show the line
            new_x = self.player2.rect.x + dx
            new_y = self.player2.rect.y + dy
            new_rect = pygame.Rect(new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
            if not any(obstacle.collides_with_circle(new_x, new_y, PLAYER_SIZE // 2) for obstacle in obstacles):
                self.player2.rect.center = (new_x, new_y)

# Obstacle class
class Obstacle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.center = (x + width // 2, y + height // 2)

    def draw(self):
        pygame.draw.rect(window, BLACK, self.rect)

    def collides_with_circle(self, x, y, radius):
        # Calculate distance between obstacle's center and circle's center
        dist_x = abs(self.center[0] - x)
        dist_y = abs(self.center[1] - y)

        # If distance is greater than half the width or height of the obstacle, it's not colliding
        if dist_x > (self.rect.width / 2 + radius):
            return False
        if dist_y > (self.rect.height / 2 + radius):
            return False

        # If distance is less than half the width or height of the obstacle, it's colliding
        if dist_x <= (self.rect.width / 2):
            return True
        if dist_y <= (self.rect.height / 2):
            return True

        # Check collision with corner of the obstacle
        corner_dist_sq = (dist_x - self.rect.width / 2) ** 2 + (dist_y - self.rect.height / 2) ** 2
        return corner_dist_sq <= (radius ** 2)
    
    def collides_with_line(self, x1, y1, x2, y2):
        # Check if the line segment intersects with the obstacle
        line_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        if not line_rect.colliderect(self.rect):
            return False

        # Check each corner of the obstacle to see if it's on the line segment
        corners = [(self.rect.left, self.rect.top),
                   (self.rect.right, self.rect.top),
                   (self.rect.left, self.rect.bottom),
                   (self.rect.right, self.rect.bottom)]
        for corner in corners:
            if self.point_on_line_segment(corner[0], corner[1], x1, y1, x2, y2):
                return True

        # Check each side of the obstacle to see if it intersects with the line segment
        sides = [(self.rect.left, self.rect.top, self.rect.left, self.rect.bottom),
                 (self.rect.left, self.rect.top, self.rect.right, self.rect.top),
                 (self.rect.right, self.rect.top, self.rect.right, self.rect.bottom),
                 (self.rect.left, self.rect.bottom, self.rect.right, self.rect.bottom)]
        for side in sides:
            if self.segments_intersect(x1, y1, x2, y2, *side):
                return True

        return False

    def point_on_line_segment(self, x, y, x1, y1, x2, y2):
        return min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2)

    def segments_intersect(self, x1, y1, x2, y2, x3, y3, x4, y4):
        # Calculate the orientation of three points
        def orientation(px, py, qx, qy, rx, ry):
            val = (qy - py) * (rx - qx) - (qx - px) * (ry - qy)
            if val == 0:
                return 0
            return 1 if val > 0 else 2

        # Check if two line segments intersect
        o1 = orientation(x1, y1, x2, y2, x3, y3)
        o2 = orientation(x1, y1, x2, y2, x4, y4)
        o3 = orientation(x3, y3, x4, y4, x1, y1)
        o4 = orientation(x3, y3, x4, y4, x2, y2)

        if o1 != o2 and o3 != o4:
            return True

        # Special Cases
        if o1 == 0 and self.point_on_line_segment(x3, y3, x1, y1, x2, y2):
            return True
        if o2 == 0 and self.point_on_line_segment(x4, y4, x1, y1, x2, y2):
            return True
        if o3 == 0 and self.point_on_line_segment(x1, y1, x3, y3, x4, y4):
            return True
        if o4 == 0 and self.point_on_line_segment(x2, y2, x3, y3, x4, y4):
            return True

        return False

# Create players, leash, and obstacles
player1 = Main_Player(50, 50)
player2 = Secondary_Player(50, 50, color=BLUE)  # Second player attached to the first
player1.update_other_player(player2)
player2.update_other_player(player1)
leash = Leash(player1, player2, LEASH_MAX_LENGTH)

# Generate random obstacles
obstacles = []
NUM_OBSTACLES = 30
for _ in range(NUM_OBSTACLES):
    obstacle_width = random.randint(30, 100)
    obstacle_height = random.randint(30, 100)
    obstacle_x = random.randint(0, WIDTH - obstacle_width)
    obstacle_y = random.randint(0, HEIGHT - obstacle_height)
    obstacles.append(Obstacle(obstacle_x, obstacle_y, obstacle_width, obstacle_height))

# Create the local environment window
local_env_width = LEASH_MAX_LENGTH * 2 + 50
local_env_height = LEASH_MAX_LENGTH * 2 + 50
local_env_window = pygame.Surface((local_env_width, local_env_height))

# Goal class
class Goal:
    def __init__(self, x, y, size=20, color=GREEN):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color

    def draw(self):
        pygame.draw.rect(window, self.color, self.rect)

# Create the goal
goal = Goal(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20))

# Main game loop
running = True
goal_reached = False
while running:
    window.fill(WHITE)
    # local_env_window.fill(WHITE)  # Clear the local environment window

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # Draw obstacles
    for obstacle in obstacles:
        obstacle.draw()

    # Get the state of all keys
    keys = pygame.key.get_pressed()

    # Move player 1
    dx, dy = 0, 0
    if keys[pygame.K_LEFT]:
        dx = -PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        dx = PLAYER_SPEED
    if keys[pygame.K_UP]:
        dy = -PLAYER_SPEED
    if keys[pygame.K_DOWN]:
        dy = PLAYER_SPEED
    player1.move(dx, dy)

    # Update leash position
    leash.update()

    # Draw player 1, player 2, and leash
    player1.draw()
    player2.draw()
    leash.draw()

    # Draw the goal
    goal.draw()

    # Update the local environment rectangle around player 1
    local_env_rect = pygame.Rect(player1.rect.centerx - LEASH_MAX_LENGTH - 5, player1.rect.centery - LEASH_MAX_LENGTH - 5, local_env_width, local_env_height)

     # Check if the goal is in the local environment of the main player
    if not goal_reached and local_env_rect.colliderect(goal.rect):
        # Check if the goal is within 10 units of the main player
        distance_to_goal = math.sqrt((player1.rect.centerx - goal.rect.centerx) ** 2 + (player1.rect.centery - goal.rect.centery) ** 2)
        if distance_to_goal <= LEASH_MAX_LENGTH:
            # End the game
            goal_reached = True
            print("You reached the goal!")
            goal_text = FONT.render("You reached the goal!", True, GREEN)
            window.blit(goal_text, (WIDTH // 2 - goal_text.get_width() // 2, HEIGHT // 2 - goal_text.get_height() // 2))
            pygame.display.update()
            pygame.time.wait(5000)  # Wait for 5 seconds

    # # Draw local environment around player 1
    # local_env_window.blit(window, (0, 0), local_env_rect)  # Blit the portion of the main window onto the local environment window
    # pygame.draw.rect(local_env_window, GREEN, local_env_window.get_rect(), 2)  # Draw a border around the local environment window

    # # Draw the local environment window onto the main window
    # window.blit(local_env_window, (WIDTH - local_env_width - 10, HEIGHT - local_env_height - 10))

    # Update display
    pygame.display.update()

    # Check if the goal has been reached and exit the game after 5 seconds
    if goal_reached:
        pygame.time.wait(5000)  # Wait for 5 seconds
        running = False

    # Limit frames per second
    pygame.time.Clock().tick(30)

# Quit Pygame
pygame.quit()
sys.exit()
