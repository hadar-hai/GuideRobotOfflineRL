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
FONT = pygame.font.Font(None, 36)

# Create the game window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Map Game")

# Player class
class Player:
    def __init__(self, x, y, color=RED, player2: 'Player' = None):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.color = color
        self.player2 = player2

    def draw(self):
        pygame.draw.circle(window, self.color, self.rect.center, PLAYER_SIZE // 2)

    def move(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
        if not any(obstacle.collides_with_circle(new_rect.centerx, new_rect.centery, PLAYER_SIZE // 2) for obstacle in obstacles) and not any(obstacle.collides_with_line(new_rect.centerx, new_rect.centery, self.player2.rect.centerx, self.player2.rect.centery) for obstacle in obstacles):
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
player2 = Player(50, 50, color=BLUE)  # Second player attached to the first
player1 = Player(50, 50, player2=player2)
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

# Main game loop
running = True
collision_message = False
while running:
    window.fill(WHITE)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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

    # Draw obstacles
    for obstacle in obstacles:
        obstacle.draw()

    # Draw player 1, player 2, and leash
    player1.draw()
    player2.draw()
    leash.draw()
    
    # Update display
    pygame.display.update()

    # Limit frames per second
    pygame.time.Clock().tick(100)

# Quit Pygame
pygame.quit()
sys.exit()
