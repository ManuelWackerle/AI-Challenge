from gameobjects import GameObject
from move import Move, Direction
import logging
import random
import pickle


class AgentRL_learn:
    end = 0
    board = None
    state = []
    last_action = 0
    last_food = [0, 0]
    Q = []
    v = 0.8 #discount factor
    a = 0.5 #learning rate
    reward_food = 10
    reward_death = -1
    reward_standard = 0
    board_height = 5
    board_width = 5

    def __init__(self, width, height):
        self.board_height = height
        self.board_width = width
        self.Q = []
        for i in range(0, width*height):
            l1 = []
            self.Q.append(l1)
            for j in range(4):
                l2 = []
                self.Q[i].append(l2)
                for k in range(8):
                    l3 = []
                    self.Q[i][j].append(l3)
                    for l in range(8):
                        l4 = []
                        self.Q[i][j][k].append(l4)
                        for m in range(3):
                            self.Q[i][j][k][l].append(0)
    logging.basicConfig(filename='rl_info.log', filemode='w', level=logging.NOTSET)

    def get_move(self, board, score, turns_alive, turns_to_starve, direction, head_position, body_parts):
        # if score == 50:
        #     print("Changed Standard Reward!")
        #     self.reward_standard = -0.1
        if score >= 1000:
            return Move.STRAIGHT
        self.board = board
        food = self.scan_food(board)
        state = [self.node_l(head_position), self.direct_num(direction), self.food_direction(head_position, food)]
        self.state = state
        int_move = 0
        log = ' '.join(["STATE... values: ", str([state[0], state[1], state[2]]), " q_values:", str(self.Q[state[0]][state[1]][state[2]]), " position", str(self.node_xy(state[0])),"heading", str(direction)])
        logging.info(log)
        if self.Q[state[0]][state[1]][state[2]] == [0, 0, 0]:
            int_move = random.randint(0, 2)
            log2 = ' '.join(["unknown state. random move made: ", str(int_move)])
            logging.info(log2)
        else:
            log3 = ' '.join(["State recognised: ", str(self.Q[state[0]][state[1]][state[2]])])
            logging.info(log3)
            explore = random.randint(0, 4)
            if explore == 0:
                min = 100
                for i in range(3):
                    q_value = self.get_Q(state, i)
                    if q_value >= 0 and q_value < min:
                        min = q_value
                        int_move = i
                logging.info("Exploring: " + str(int_move))
            else:
                int_move = self.maxa(state)
        n_state = self.transition_function(state, int_move)
        new_pos = n_state[0]
        log4 = ' '.join(["Going for move: ", str(int_move), " this leads to", str(n_state), "with postion", str(new_pos)])
        logging.info(log4)
        self.last_action = int_move
        self.update_Q(state, int_move, n_state)
        logging.info("State after update: " + str(self.Q[state[0]][state[1]][state[2]]) + "\n\n")
        move = self.map_move(int_move)
        return move




    def on_die(self, head_position, board, score, body_parts):
        if score >= 500:
            self.end += 1
            print("SCORE OF 500 ACHIEVED AGENT LEARNING COMPLETE")
            file_object = open("Agent005", 'wb')
            pickle.dump(self.Q, file_object)
            file_object.close()
            if self.end == 2:
                print("hello" + 1)



    def scan_food(self, board):
        for x in range(0, len(board)):
            for y in range(0, len(board[0])):
                if board[x][y] == GameObject.FOOD:
                    self.last_food = [x, y]
                    return [x, y]
        return [-1,-1]

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
        pos_reward = n_state[0]
        if n_state[3]:
            q_prime = 0
        else:
            change = self.node_l(n_state[0])
            n_state[0] = change
            q_prime = self.maxa(n_state)
        q_value = (1 - self.a) * self.get_Q(state, action) + self.a*(self.r_func(pos_reward) + self.v * q_prime)
        self.set_Q(state, action, q_value)


    def get_Q(self, state, action):
        q_value = self.Q[state[0]][state[1]][state[2]][action]
        return q_value
    """self.Q[node_l][direct_num][food][a]
       a = 0: striaght, 1: left, 2: right"""

    def set_Q(self, state, action, q_value):
        self.Q[state[0]][state[1]][state[2]][action] = q_value

    def maxa(self, state):
        max_q = -10
        max_a = 0
        for i in range(3):
            q_value = self.get_Q(state, i)
            if q_value > max_q:
                max_q = q_value
                max_a = i
        return max_a

    def transition_function(self, state, action):
        node_xy = self.node_xy(state[0])
        vector = self.vector_move(state[1], action)
        terminal = True
        x = node_xy[0] + vector[0]
        y = node_xy[1] + vector[1]
        if (0 <= x < self.board_width and 0 <= y < self.board_height) and self.board[x][y] == GameObject.EMPTY:
            terminal = False
        new_direction = self.new_direction(state[1], action)
        food_direction = self.food_direction([x, y], self.last_food)
        return [[x, y], new_direction, food_direction, terminal]

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
        vector = [0,0]
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
        """
        • Model of the state space.
        • Reward function.
        • Discount factor.
        • Using U-learning or Q-learning and why.
        • Learning parameter(s)
        This function indicates whether the board should be redrawn. Not drawing to the board increases the number of
        games that can be played in a given time. This is especially useful if you want to train you agent. The
        function is called before the get_move function.

        :return: True if the board should be redrawn, False if the board should not be redrawn.
        """
        return True

    def should_grow_on_food_collision(self):
        return False

def main():
    agent = AgentRL(3,3)
    print(agent.flipmove(0))
    print(agent.flipmove(1))
    print(agent.flipmove(2))



if __name__ == '__main__':
    main()

