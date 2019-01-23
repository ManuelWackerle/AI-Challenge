from gameobjects import GameObject
from move import Move, Direction
import logging
import random
import pickle


class AgentRL2_learn:
    end = 0
    board = None
    state = []
    last_action = 0
    last_food = [0, 0]
    Q = []
    v = 0.8  # discount factor
    a = 0.5  # learning rate
    reward_food = 16.
    reward_death = -16.
    reward_standard = -0.64
    board_height = 5
    board_width = 5
    diecount = 0
    tail = [0, 0]

    def __init__(self, width, height):
        self.board_height = height
        self.board_width = width

        agent = 'Agent253'
        q_object = open(agent, 'rb')
        self.Q = pickle.load(q_object)
        q_object.close()

        # self.Q = []
        # for i in range(0, width * height):
        #     l1 = []
        #     self.Q.append(l1)
        #     for j in range(4):
        #         l2 = []
        #         self.Q[i].append(l2)
        #         for k in range(3):
        #             l3 = []
        #             self.Q[i][j].append(l3)
        #             for l in range(3):
        #                 l4 = []
        #                 self.Q[i][j][k].append(l4)
        #                 for m in range(3):
        #                     self.Q[i][j][k][l].append(0)

    logging.basicConfig(filename='rl_info.log', filemode='w', level=logging.NOTSET)

    def get_move(self, board, score, turns_alive, turns_to_starve, direction, head_position, body_parts):
        # if score == 50:
        #     print("Changed Standard Reward!")
        #     self.reward_standard = -0.1
        if score >= 1000:
            return Move.STRAIGHT
        self.board = board
        food = self.scan_food(board)
        direct_num = self.direct_num(direction)
        food_direct = self.relative_food_direction(head_position, food, direct_num)
        tail_direct = 0
        """____________________using tail tip direction_________________________________"""
        if len(body_parts) > 0:
            tail = body_parts[-1]
            self.tail = tail
            tail_direct = self.relative_tail_direction(head_position, tail, direct_num)
        state = [self.node_l(head_position), direct_num, food_direct, tail_direct]
        """_____________________using position of food_________________________________"""
        # food_dist = self.food_dist(head_position, food)
        # state = [self.node_l(head_position), direct_num, food_direct, food_dist]

        self.state = state
        int_move = 0
        # log = ' '.join(["STATE... values: ", str([state[0], state[1], state[2], state[3]]), " q_values:",
        #                 str(self.Q[state[0]][state[1]][state[2]][state[3]]), " position", str(self.node_xy(state[0])), "heading",
        #                 str(direction)])
        # logging.info(log)
        if self.Q[state[0]][state[1]][state[2]][state[3]] == [0, 0, 0]:
            int_move = random.randint(0, 2)
            # log2 = ' '.join(["unknown state. random move made: ", str(int_move)])
            # logging.info(log2)
        else:
            # log3 = ' '.join(["State recognised: ", str(self.Q[state[0]][state[1]][state[2]][state[3]])])
            # logging.info(log3)
            explore = random.randint(0, 3)
            if explore == 0:
                int_move = random.randint(0, 2)
            elif explore == 1:
                int_move = food_direct
                # logging.info("Exploring: " + str(int_move))
            else:
                int_move = self.maxa(state)
        n_state = self.transition_function(state, int_move)
        new_pos = n_state[4]
        # log4 = ' '.join(
            # ["Going for move: ", str(int_move), " this leads to", str(n_state), "with postion", str(new_pos)])
        # logging.info(log4)
        self.last_action = int_move
        self.update_Q(state, int_move, n_state)
        logging.info("State after update: " + str(self.Q[state[0]][state[1]][state[2]][state[3]]) + "\n\n")
        move = self.map_move(int_move)
        return move

    def on_die(self, head_position, board, score, body_parts):
        self.diecount += 1
        print(self.diecount)
        if score >= 500 or self.diecount == 400:
            self.diecount = 0
            self.end += 1
            print("AGENT LEARNING COMPLETE")
            file_object = open("Agent253", 'wb')
            pickle.dump(self.Q, file_object)
            file_object.close()


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

    def num_direct(self, num):
        if num == 0:
            return Direction.NORTH
        elif num == 1:
            return Direction.EAST
        elif num == 2:
            return Direction.SOUTH
        elif num == 3:
            return Direction.WEST

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

    def relative_tail_direction(self, head, tail, direction):
        xf = tail[0]
        yf = tail[1]
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

    def food_dist(self, head, food):
        dist = self.h_score(head, food)
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


    def r_func(self, node_xy):
        board = self.board
        x = node_xy[0]
        y = node_xy[1]
        if x < 0 or x >= len(board) or y < 0 or y >= len(board[0]) or board[x][y] == GameObject.WALL:
            return self.reward_death
        elif board[x][y] == GameObject.FOOD:
            logging.info("A  REWARD WAS GIVEN OF: " + str(self.reward_food))
            return self.reward_food
        else:
            return self.reward_standard

    def update_Q(self, state, action, n_state):
        # self.last_nodes.append(n_state[0])
        # pop = self.last_nodes.pop(0)
        pos_reward = n_state[0]
        # if pop == n_state[0]:
        #     print("hello")
        if n_state[4]:
            q_prime = 0
        else:
            change = self.node_l(n_state[0])
            n_state[0] = change
            q_prime = self.maxq(n_state)
        old = self.get_Q(state, action)
        q_value = (1 - self.a) * old + self.a * (self.r_func(pos_reward) + self.v * q_prime)
        self.set_Q(state, action, q_value)

    def get_Q(self, state, action):
        return self.Q[state[0]][state[1]][state[2]][state[3]][action]

    """self.Q[node_l][direct_num][food][a]
       a = 0: striaght, 1: left, 2: right"""

    def set_Q(self, state, action, q_value):
        self.Q[state[0]][state[1]][state[2]][state[3]][action] = q_value

    def maxa(self, state):
        max_q = -10
        max_a = 0
        for i in range(3):
            q_value = self.get_Q(state, i)
            if q_value > max_q:
                max_q = q_value
                max_a = i
        return max_a

    def maxq(self, state):
        max_q = -25
        for i in range(3):
            q_value = self.get_Q(state, i)
            if q_value > max_q:
                max_q = q_value
        return max_q

    def transition_function(self, state, action):
        node_xy = self.node_xy(state[0])
        vector = self.vector_move(state[1], action)
        terminal = True
        x = node_xy[0] + vector[0]
        y = node_xy[1] + vector[1]
        if (0 <= x < self.board_width and 0 <= y < self.board_height) and self.board[x][y] == GameObject.EMPTY:
            terminal = False
        new_direction = self.new_direction(state[1], action)
        food_direction = self.relative_food_direction([x, y], self.last_food, new_direction)
        # food_dist = self.food_dist([x, y], self.last_food)
        tail_direct = self.relative_tail_direction([x, y], self.tail, new_direction)
        return [[x, y], new_direction, food_direction, tail_direct, terminal]

    def node_l(self, node_xy):
        node_l = node_xy[1] * self.board_height + node_xy[0]
        return node_l

    def node_xy(self, node_l):
        node_xy = [0, 0]
        node_xy[0] = node_l % self.board_height
        node_xy[1] = node_l // self.board_height

        return node_xy

    def map_move(self, relative_move):
        if relative_move == 0:
            return Move.STRAIGHT
        elif relative_move == 1:
            return Move.LEFT
        elif relative_move == 2:
            return Move.RIGHT
        else:
            print("serious bug somewhere... damn :,(")

    def flipmove(self, move):
        return 1 - ((move + 1) % 3)

    def vector_move(self, direction, move_012):
        move = self.flipmove(move_012)
        vector = [0, 0]
        if direction == 0:
            vector[0] = move
            vector[1] = -((move + 1) % 2)
        elif direction == 1:
            vector[0] = (move + 1) % 2
            vector[1] = move
        elif direction == 2:
            vector[0] = - move
            vector[1] = (move + 1) % 2
        elif direction == 3:
            vector[0] = -((move + 1) % 2)
            vector[1] = - move
        return vector

    def new_direction(self, direction, map_move):
        if map_move == 1:
            new_direction = (direction - 1) % 4
        elif map_move == 2:
            new_direction = (direction + 1) % 4
        else:
            new_direction = direction
        return new_direction

    def should_redraw_board(self):
        return True

    def should_grow_on_food_collision(self):
        return False


def main():
    agent = 6


if __name__ == '__main__':
    main()

