import random
from global_parameters import *
from math import sqrt

class Agent:
    '''
    General agent class. Here we can modify agent inputs, outputs and general functions.
    Every agent should have a method called get_state_set_action
    '''

    def __init__(self, player_id, obstacles=None, goal=None):
        self.player_ID = player_id  # player 1 (robot) or player 2 (simulated human)
        self.obstacles = obstacles
        self.goal = goal


class RandomAgent(Agent):
    def __init__(self, obstacles = None, goal = None):
        super().__init__(obstacles, goal)

    def get_state_set_action(self, state=None):
        '''
        :param state: positions of player 1 and player 2 (format?)
        :return: dx, dy, direction
        '''
        actions = [0, 1, 2, 3, 4]
        dx = 0
        dy = 0
        selected_action = random.choice(actions)

        if selected_action == 0:
            #left
            dx = -PLAYER_SPEED
        elif selected_action == 1:
            #right
            dx = PLAYER_SPEED
        elif selected_action == 2:
            #up
            dy = PLAYER_SPEED
        elif selected_action == 3:
            #down
            dy = -PLAYER_SPEED

        return dx, dy, selected_action

class EpsilonLeashFollow(Agent):
    # This agent makes a random step in the chance of epsilon,
    # Otherwise it follows the leash (if there is no leash signal it stays still).
    # This agent doesn't care which player_id it is, but only makes sense in replacing the human player!

    def __init__(self, obstacles = None, goal = None):
        super().__init__(obstacles, goal)
        self.epsilon = 0.12
        self.no_of_steps = 3  # how many steps towards a taught leash
        self.current_state = None
        self.steps_remaining = 0

        # defaults
        self.dx = 0
        self.dy = 0
        self.action = 4

    def get_state_set_action(self, state=None):
        self.current_state = state
        # initialize action to noop
        dx = 0
        dy = 0
        action = 4


        # choose a random action in an epsilon chance
        if random.random() < self.epsilon:
            dx, dy, action = self.choose_random_action()
        else:
            # if there are steps remaining - continue moving in that direction
            if self.steps_remaining > 0:
                dx = self.dx  # from before
                dy = self.dy  # from before
                action = self.action  # from before
                self.steps_remaining = self.steps_remaining - 1
            else:
                if self.is_leash_at_max():
                    # if leash is at maximum length - follow it
                    self.steps_remaining = self.no_of_steps  # reset no of steps
                    dx, dy, action = self.follow_leash_direction()
                    self.dx = dx
                    self.dy = dy
                    self.action = action
                    pass
                else: # leash is not at max - don't move
                    pass
        return dx, dy, action

    def follow_leash_direction(self):
        # defaults
        dx = 0
        dy = 0
        action = 4

        # get player locations
        player1_x = self.current_state[0]
        player1_y = self.current_state[1]
        player2_x = self.current_state[2]
        player2_y = self.current_state[3]

        # determine which direction (up-down / left-right) is most dominant
        if abs(player1_x - player2_x) > abs(player1_y - player2_y):
            # x-axis is dominant - move right or left
            if player1_x < player2_x: # player 1 is more to the left - move left
                action = 0
                dx = -PLAYER_SPEED
            else: # move left
                action = 1
                dx = PLAYER_SPEED
        else:
            # y-axis is dominant - move up or down
            if player1_y > player2_y: # player 1 is higher - go up
                action = 2
                dy = PLAYER_SPEED
            else: #move down
                action = 3
                dy = -PLAYER_SPEED

        return dx, dy, action


    def is_leash_at_max(self):
        '''
        checks the state to see if the leas is at max
        :return: True or false
        '''
        leash_at_max = False

        # get player locations
        player1_x = self.current_state[0]
        player1_y = self.current_state[1]
        player2_x = self.current_state[2]
        player2_y = self.current_state[3]

        #calculate the distance between them:
        dist = sqrt((player1_x - player2_x)**2 + (player1_y-player2_y)**2)
        if dist >= LEASH_MAX_LENGTH:
            leash_at_max = True

        return leash_at_max


    def choose_random_action(self):
        '''
        chooses a random action
        :return: dx, dy, selected action
        '''
        actions = [0, 1, 2, 3, 4]
        dx = 0
        dy = 0
        action = 4  # noop = default
        selected_action = random.choice(actions)

        if selected_action == 0:
            # left
            dx = -PLAYER_SPEED
        elif selected_action == 1:
            # right
            dx = PLAYER_SPEED
        elif selected_action == 2:
            # up
            dy = PLAYER_SPEED
        elif selected_action == 3:
            # down
            dy = -PLAYER_SPEED

        return dx, dy, selected_action

class Roomba(Agent):
    # This agent picks a random direction and makes a finite amount of steps in that direction
    def __init__(self, obstacles=None, goal=None):
        super().__init__(obstacles, goal)
        self.max_steps = 100
        self.steps_remaining = 0
        self.current_action = 4 # default
        self.dx = 0
        self.dy = 0

    def get_state_set_action(self, state=None):
        action = 4
        dx = 0
        dy = 0

        if self.steps_remaining > 0:
            # if there are steps remaining - continue moving where you were
            dx = self.dx
            dy = self.dy
            action = self.current_action

            self.steps_remaining = self.steps_remaining - 1

        else:
            # otherwise - randomize direction and move
            self.steps_remaining = self.max_steps

            directions = [0, 1, 2, 3]
            action = random.choice(directions)

            if action == 0:
                # left
                dx = -PLAYER_SPEED
            elif action == 1:
                # right
                dx = PLAYER_SPEED
            elif action == 2:
                # up
                dy = PLAYER_SPEED
            elif action == 3:
                # down
                dy = -PLAYER_SPEED

            self.current_action = action
            self.dx = dx
            self.dy = dy

        return dx, dy, action

class GoalFollow(Agent):
    # This robot agent goes in the direction of the goal.
    # if this robot collides with an obstacle - it escapes it
    def __init__(self, obstacles = None, goal = None):
        super().__init__(obstacles, goal)
        self.is_escaping_obstacle = False
        self.escape_action = 4
        self.escape_dx = 0
        self.escape_dy = 0

        self.obstacles = obstacles
        self.goal = goal

    def get_state_set_action(self, state=None):
        self.current_state = state

        # defaults
        action = 4
        dx = 0
        dy =0

        self.player1_x = state[0]

        if self.is_escaping_obstacle:
            # if we are in an obstacle escape sequence - move
            action = self.escape_action
            dx = self.escape_dx
            dy = self.escape_dy
        else:
            if self.collision_detection():
                # if we are colliding with obstacle - initiate escape
                self.is_escaping_obstacle = True
                dx, dy, action = self.choose_random_action()
                self.escape_action = action
                self.escape_dx = dx
                self. escape_dy = dy
            else:
                # else: move in the direction of the goal
                dx, dy, action = self.move_to_goal()

        return dx, dy, action

    def move_to_goal(self):
        '''
        chooses an action and direction based on where the target and player 2 (human) are.
        :return: dx, dy, action
        '''
        # defaults
        action = 4
        dx = 0
        dy = 0

        # get player and goal positions
        player2_x = self.current_state[2]
        player2_y = self.current_state[3]
        goal_x = self.goal.rect.centerx
        goal_y = self.goal.rect.centery

        # determine which axis is stronger - up/down or left\right
        if abs(player2_x-goal_x) > abs(player2_y-goal_y):
            # move left or right
            if goal_x < player2_x: #goal is to the left - move left
                action = 0
                dx = -PLAYER_SPEED
            else: #goal is to the right - move right
                action = 1
                dx = PLAYER_SPEED
        else:
            # move up or down
            if goal_y > player2_y: #goal is upwards - move up
                action = 2
                dy = PLAYER_SPEED
            else: #goal is downwards - move down
                action = 3
                dy = -PLAYER_SPEED

        return dx, dy, action



    def collision_detection(self):
        '''
        check for collision of the robot agent (player 1)
        :return: True or False
        '''

        # get player locations
        player1_x = self.current_state[0]
        player1_y = self.current_state[1]

        temp_rect = pygame.Rect(player1_x, player1_y, PLAYER_SIZE, PLAYER_SIZE)
        for obstacle in self.obstacles:
            if temp_rect.colliderect(obstacle.rect):
                return True

        return False

    def choose_random_action(self):
        '''
        chooses a random action
        :return: dx, dy, selected action
        '''
        actions = [0, 1, 2, 3]
        dx = 0
        dy = 0
        action = 4  # noop = default
        selected_action = random.choice(actions)

        if selected_action == 0:
            # left
            dx = -PLAYER_SPEED
        elif selected_action == 1:
            # right
            dx = PLAYER_SPEED
        elif selected_action == 2:
            # up
            dy = PLAYER_SPEED
        elif selected_action == 3:
            # down
            dy = -PLAYER_SPEED

        return dx, dy, selected_action
