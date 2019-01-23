from gameobjects import GameObject
from move import Move, Direction
import logging
import pickle


class AgentRL_run:
    board = None
    state = []
    last_action = 0
    last_food = [0, 0]
    Q = []
    board_height = 5
    board_width = 5

    def __init__(self, width, height, agent_number):
        self.board_height = height
        self.board_width = width
        agent = 'Agent10' + str(agent_number)
        q_object = open(agent, 'rb')
        self.Q = pickle.load(q_object)
        q_object.close()



    logging.basicConfig(filename='rl_test001.log', filemode='w', level=logging.DEBUG)

    def get_move(self, board, score, turns_alive, turns_to_starve, direction, head_position, body_parts):
        self.board = board
        food = self.scan_food(board)
        state = [self.node_l(head_position), self.direct_num(direction), self.food_direction(head_position, food)]
        self.state = state
        int_move = self.maxa(state)
        move = self.map_move(int_move)
        return move

    def on_die(self, head_position, board, score, body_parts):
        return True

    def get_Q(self, state, action):
        return self.Q[state[0]][state[1]][state[2]][action]

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

    def food_direction(self, head, food):
        xf = food[0]
        yf = food[1]
        xh = head[0]
        yh = head[1]
        if xf > xh:
            if yf > yh:
                return 1
            elif yf == yh:
                return 2
            else:
                return 3
        elif xf < xh:
            if yf > yh:
                return 7
            elif yf == yh:
                return 6
            else:
                return 5
        else:
            if yf > yh:
                return 0
            else:
                return 4

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



