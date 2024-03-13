# Map features: Obstacle, Goal, ScoreManager
# Documentation required!

from global_parameters import *

# Obstacle class
class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height=height

        self.rect = pygame.Rect(x, y, width, height)
        self.center = (x + width // 2, y + height // 2)

    def draw(self, window):
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

# Goal class
class Goal:
    def __init__(self, window, x, y, size=20, color=GREEN):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = color
        self.window = window

    def draw(self):
        pygame.draw.rect(self.window, self.color, self.rect)


class ScoreManager:
    def __init__(self):
        self.player1_score = 100  # Initial score for Player 1
        self.player2_score = 100  # Initial score for Player 2

    def update_score(self, player1, player2):
        # Update Player 1's score
        if player1.collision_flag:
            self.player1_score -= 50
            player1.collision_flag = False  # Reset flag after handling
        if player1.reached_goal_flag:
            self.player1_score += 1000
            player1.reached_goal_flag = False  # Reset flag if needed

        # Update Player 2's score
        if player2.collision_flag:
            self.player2_score -= 10
            player2.collision_flag = False  # Reset flag after handling
        if player2.reached_goal_flag:
            self.player2_score += 1000
            player2.reached_goal_flag = False  # Reset flag if needed

        # Optionally, you can have other conditions here to modify the scores

    def get_player1_score(self):
        return self.player1_score

    def get_player2_score(self):
        return self.player2_score

    def display_score(self, window, font):
        # Display Player 1's score
        player1_score_text = font.render(f"Player 1 Score: {self.get_player1_score()}", True, BLACK)
        window.blit(player1_score_text, (10, 10))  # Adjust position as needed

        # Display Player 2's score
        player2_score_text = font.render(f"Player 2 Score: {self.get_player2_score()}", True, BLACK)
        window.blit(player2_score_text, (10, 40))  # Adjust position as needed
