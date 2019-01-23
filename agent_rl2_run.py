from gameobjects import GameObject
from move import Move, Direction
import logging
import pickle


class AgentRL2run:
    board = None
    state = []
    last_action = 0
    last_food = [0, 0]
    Q = []
    board_height = 0
    board_width = 0
    moves = 0

    def __init__(self, width, height, agent_number):
        self.board_height = height
        self.board_width = width
        agent = 'Agent25' + str(agent_number)
        q_object = open(agent, 'rb')
        self.Q = pickle.load(q_object)
        q_object.close()



    logging.basicConfig(filename='rl_test001.log', filemode='w', level=logging.DEBUG)

    def get_move(self, board, score, turns_alive, turns_to_starve, direction, head_position, body_parts):
        food = self.scan_food(board)
        direct_num = self.direct_num(direction)
        food_direct = self.relative_food_direction(head_position, food, direct_num)
        food_dist = self.food_dist(head_position, food)
        state = [self.node_l(head_position), direct_num, food_direct, food_dist]
        self.state = state
        int_move = self.maxa(state)
        move = self.map_move(int_move)
        self.moves += 1
        if self.moves == 100:
            self.moves = 0
            print("Score: ", score)
        return move


    def on_die(self, head_position, board, score, body_parts):
        return True

    def get_Q(self, state, action):
        return self.Q[state[0]][state[1]][state[2]][state[3]][action]

    def maxa(self, state):
        max_q = -10
        max_a = 0
        for i in range(3):
            q_value = self.get_Q(state, i)
            if q_value > max_q:
                max_q = q_value
                max_a = i
        return max_a

    def scan_food(self, board):
        for x in range(0, len(board)):
            for y in range(0, len(board[0])):
                if board[x][y] == GameObject.FOOD:
                    self.last_food = [x, y]
                    return [x, y]
        return [-1, -1]

    def direct_num(self, direction):
        if direction == Direction.NORTH:
            return 0
        elif direction == Direction.EAST:
            return 1
        elif direction == Direction.SOUTH:
            return 2
        elif direction == Direction.WEST:
            return 3

    def relative_food_direction(self, head, food, direction):
        xf = food[0]
        yf = food[1]
        xh = head[0]
        yh = head[1]
        if direction == 0:
            if yf < yh:
                return 0
            elif xf < xh:
                return 1
            else:
                return 2
        elif direction == 1:
            if xf > xh:
                return 0
            elif yf > yh:
                return 2
            else:
                return 1
        elif direction == 2:
            if yf > yh:
                return 0
            elif xf > xh:
                return 1
            else:
                return 2
        elif direction == 3:
            if xf < xh:
                return 0
            elif yf < yh:
                return 2
            else:
                return 1

    def node_l(self, node_xy):
        node_l = node_xy[1] * self.board_height + node_xy[0]
        return node_l

    @staticmethod
    def map_move(relative_move):
        if relative_move == 0:
            return Move.STRAIGHT
        elif relative_move == 1:
            return Move.LEFT
        elif relative_move == 2:
            return Move.RIGHT
        else:
            print("serious bug somewhere... damn :,(")

    def should_redraw_board(self):
        return True

    def should_grow_on_food_collision(self):
        return False


    def food_dist(self, head, food):
        dist = self.h_score(head, food)
        if self.board_height <= 10:
            if dist >= 6:
                return 5
            else:
                return dist - 1
        else:
            if dist > 16:
                return 9
            elif dist > 12:
                return 8
            elif dist > 9:
                return 7
            elif dist > 7:
                return 6
            elif dist > 5:
                return 5
            else:
                return dist - 1

    def h_score(self, node, goal):
        return abs(goal[0] - node[0]) + abs(goal[1] - node[1])

