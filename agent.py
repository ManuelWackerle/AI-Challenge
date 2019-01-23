from gameobjects import GameObject
from move import Move, Direction
from timeit import default_timer as timer
import logging
"""TOP SCORES:
Score achieved: 130. Turns it took: 1283
Score achieved: 144. Turns it took: 1551
Score achieved: 137. Turns it took: 1329
Score achieved: 140. Turns it took: 1448
Score achieved: 141. Turns it took: 1526
Score achieved: 150. Turns it took: 1662
Score achieved: 139. Turns it took: 1367
"""


class Agent:
    type = None
    known = False
    path = []
    trail = []
    tail_tip = [0, 0]
    a_star_count = 0
    closed_len = 0

    def __init__(self):
        type = 1




    def get_move(self, board, score, turns_alive, turns_to_starve, direction, head_position, body_parts):
        # if len(body_parts) < 20:
        start = timer()
        if len(self.path) > 0:
            print("First if")
            relative_move = self.path.pop(0)
            move = self.map_move(relative_move)
        else:
            print("Second if")
            board_copy = self.board_copy(board, head_position, body_parts)
            food_pos = self.scan_food(board, head_position)
            self.path = self.a_star_search(head_position, food_pos, board_copy, direction)
            relative_move = self.path.pop(0)
            move = self.map_move(relative_move)

        end = timer()
        print("Time: ", end - start)
        return move

        # else:
        #     if len(self.path) > 0:
        #         relative_move = self.path.pop(0)
        #         move = self.map_move(relative_move)
        #     else:
        #         print(body_parts)
        #         board_copy = self.board_copy(board, head_position, body_parts)
        #         self.path = self.a_star_search(head_position, tail_tip, board_copy, direction)
        #         logging.info(board_copy)
        #         logging.info("tail tip:")
        #         logging.info(tail_tip)
        #         logging.info(self.tail_tip)
        #         relative_move = self.path.pop(0)
        #         move = self.map_move(relative_move)
        #     return move


    def board_copy(self, board, head_postion, body_parts):
        movable = []
        for x in range(0, len(board)):
            list = []
            for y in range(0, len(board[0])):
                if board[x][y] == GameObject.EMPTY or board[x][y] == GameObject.FOOD:
                    list.append(1)
                else:
                    list.append(0)
            movable.append(list)
        snake_size = len(body_parts)
        if snake_size > 5:
            tail_tip = body_parts[snake_size - 1]
            n = 1
            h_score_tail = self.h_score(tail_tip, head_postion)
            while n < h_score_tail:
                x = tail_tip[0]
                y = tail_tip[1]
                movable[x][y] = 1
                n += 1
                tail_tip = body_parts[snake_size - n]
                self.tail_tip = tail_tip
                h_score_tail = self.h_score(tail_tip, head_postion)
        return movable

    def not_contains(self, frontier, node):
        for x in range(0, len(frontier)):
            if node == frontier[x][0]:
                return False
        return True

    def map_move(self, relative_move):
        if relative_move == 0:
            return Move.STRAIGHT
        elif relative_move == -1:
            return Move.LEFT
        elif relative_move == 1:
            return Move.RIGHT
        else:
            print("Something went wrong: check relative_move")

    def space_filler(self, head, board, direction):
        x = head[0]
        y = head[1]
        for i in [1, -1]:
            if (0 <= x + i < len(board) and board[x + i][y] == 1 ): #and not((direction == Direction.NORTH and i == -1) or (direction == Direction.SOUTH and i == 1)
                    move = self.relative_move(direction, [i, 0])
                    return [move]
        for j in [1, -1]:
            if 0 <= y + j < len(board[0]) and board[x][y + j] == 1:
                    move = self.relative_move(direction, [0, j])
                    return [move]
        return [0]

    def a_star_search(self, head, goal, board, direction):
        self.a_star_count += 1
        new_direction = direction
        closed = []
        explore = [0, 1, 0, -1, 0]
        # Format = [node, g_score, f_score, relative_move list, direction]
        frontier = [[head, 0, self.f_score(head, 0, goal), [], new_direction]]
        current = frontier[0]
        n = 0
        while len(frontier) > 0 and n < 2500:
            n += 1
            min_f_score = 100
            for node in frontier:
                if node[0] == goal:
                    self.closed_len += len(closed)
                    # print("Goal Node Found!")
                    return node[3]

                if node[2] <= min_f_score:
                    current = node
                    min_f_score = current[2]
            if current in frontier:
                frontier.remove(current)
                closed.append(current)
            x = current[0][0]
            y = current[0][1]
            new_g = current[1] + 1
            moves = current[3]
            old_direction = current[4]
            for c in range(0, 4):
                i = explore[c]
                j = explore[c + 1]
                new = [x + i, y + j]
                if 0 <= x + i < len(board) and 0 <= y + j < len(board[0]) and board[x + i][y + j] != 0:
                    move = self.relative_move(old_direction, [i, j])
                    new_direction = self.new_direction(old_direction, move)
                    new_moves = moves.copy()
                    new_moves.append(move)
                    new_node = [new, new_g, self.f_score(new, new_g, goal), new_moves, new_direction]
                    if self.not_contains(closed, new) and self.not_contains(frontier, new):
                        frontier.append(new_node)
        self.closed_len += len(closed)
        # print("Food not found, going into space filler mode:")
        return self.space_filler(head, board, direction)


    def f_score(self, node, g_score, goal):
        return self.h_score(node, goal) + g_score

    def h_score(self, node, goal):
        return abs(goal[0] - node[0]) + abs(goal[1] - node[1])

    def scan_food(self, board, head):
        food_list = []
        for x in range(0, len(board)):
            for y in range(0, len(board[0])):
                if board[x][y] == GameObject.FOOD:
                    food_list.append([x, y])
        return self.closest_food(food_list, head)

    def closest_food(self, list, head):
        min_h = 100
        best = None
        for pos in list:
            h_score = self.h_score(head, pos)
            if h_score < min_h:
                min_h = h_score
                best = pos
        return best

    def relative_move(self, direction, vector):
        # [0, -1]
        if direction == Direction.NORTH:
            move = vector[0]
        elif direction == Direction.EAST:
            move = vector[1]
        elif direction == Direction.WEST:
            move = vector[1]*(-1)
        else:
            move = vector[0]*(-1)
        return move
    # returns moves encoded by -1: Left, 0: Straight, 1: Right
    #
    def new_direction(self, direction, relative_move):
        if relative_move == -1:
            if direction == Direction.NORTH:
                new_direction = Direction.WEST
            elif direction == Direction.EAST:
                new_direction = Direction.NORTH
            elif direction == Direction.WEST:
                new_direction = Direction.SOUTH
            else:
                new_direction = Direction.EAST
        elif relative_move == 1:
            if direction == Direction.NORTH:
                new_direction = Direction.EAST
            elif direction == Direction.EAST:
                new_direction = Direction.SOUTH
            elif direction == Direction.WEST:
                new_direction = Direction.NORTH
            else:
                new_direction = Direction.WEST
        else: new_direction = direction
        return new_direction


    def dot_product_2(self, v1, v2):
        return v1[0]*v2[0] + v1[1]*v2[1]

    def dot_product_n(self, v1, v2):
        sum = 0
        for x in range(0, len(v1)):
            sum += v1[x]*v2[x]
        return sum

    def should_redraw_board(self):
        # :return: True if the board should be redrawn, False if the board should not be redrawn.
        return True

    def should_grow_on_food_collision(self):
        # :return: True if the snake should grow, False if the snake should not grow
        return True

    def on_die(self, head_position, board, score, body_parts):
        count = self.a_star_count
        nnode = self.closed_len
        if count > 0: int_av = nnode//count
        else: int_av = -1
        print("Count: ", count, "Number of nodes expanded: ", nnode, "average: ", int_av)
        self.a_star_count = 0
        self.closed_len = 0
        """This function will be called whenever the snake dies. After its dead the snake will be reincarnated into a
        new snake and its life will start over. This means that the next time the get_move function is called,
        it will be called for a fresh snake. Use this function to clean up variables specific to the life of a single
        snake or to host a funeral.

        :param head_position: (x, y) position of the head at the moment of dying.

        :param board: two dimensional array representing the board of the game at the moment of dying. The board
        given does not include information about the snake, only the food position(s) and wall(s) are listed.

        :param score: score at the moment of dying.

        :param body_parts: the array of the locations of the body parts of the snake. The last element of this array
        represents the tail and the first element represents the body part directly following the head of the snake.
        When the snake runs in its own body the following holds: head_position in body_parts.
        """


def main():

    from board import Board
    from snake import Snake
    from agent import Agent

    board_width = 30
    board_height = 30
    agent = Agent()
    snake = Snake(board_width, board_height, 1)
    board = Board(board_width, board_height, 600, 600, snake, 0, 0, True)
    board.set_game_object_at(15, 15, GameObject.FOOD)
    board.set_game_object_at(12, 16, GameObject.WALL)
    board.set_game_object_at(12, 15, GameObject.WALL)
    board.set_game_object_at(17, 11, GameObject.WALL)
    board.set_game_object_at(14, 12, GameObject.WALL)
    board.set_game_object_at(16, 12, GameObject.WALL)
    board.set_game_object_at(15, 12, GameObject.WALL)
    board.set_game_object_at(13, 12, GameObject.WALL)
    board.set_game_object_at(12, 12, GameObject.WALL)
    board.set_game_object_at(11, 12, GameObject.WALL)
    board.set_game_object_at(10, 11, GameObject.WALL)
    snake.x = 10
    snake.y = 10
    print(board.get_game_object_at(15, 15))
    print(board.get_game_object_at(12, 15))
    print(board.get_game_object_at(15, 15))
    print(board.get_game_object_at(10, 10))
    agent.a_star_search([10,10], [15,15], board.board, Direction.NORTH)




if __name__ == '__main__':
    main()

    """
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
INFO:root:tail tip:
INFO:root:(1, 21)
    
    function reconstruct_path(cameFrom, current)
    total_path := {current}
    while current in cameFrom.Keys:
        current := cameFrom[current]
        total_path.append(current)
    return total_path

function A_Star(start, goal)
    // The set of nodes already evaluated
    closedSet := {}

    // The set of currently discovered nodes that are not evaluated yet.
    // Initially, only the start node is known.
    openSet := {start}

    // For each node, which node it can most efficiently be reached from.
    // If a node can be reached from many nodes, cameFrom will eventually contain the
    // most efficient previous step.
    cameFrom := an empty map

    // For each node, the cost of getting from the start node to that node.
    gScore := map with default value of Infinity

    // The cost of going from start to start is zero.
    gScore[start] := 0

    // For each node, the total cost of getting from the start node to the goal
    // by passing by that node. That value is partly known, partly heuristic.
    fScore := map with default value of Infinity

    // For the first node, that value is completely heuristic.
    fScore[start] := heuristic_cost_estimate(start, goal)

    while openSet is not empty
        current := the node in openSet having the lowest fScore[] value
        if current = goal
            return reconstruct_path(cameFrom, current)

        openSet.Remove(current)
        closedSet.Add(current)

        for each neighbor of current
            if neighbor in closedSet
                continue		// Ignore the neighbor which is already evaluated.

            // The distance from start to a neighbor
            tentative_gScore := gScore[current] + dist_between(current, neighbor)

            if neighbor not in openSet	// Discover a new node
                openSet.Add(neighbor)
            else if tentative_gScore >= gScore[neighbor]
                continue;       

            // This path is the best until now. Record it!
            cameFrom[neighbor] := current
            gScore[neighbor] := tentative_gScore
            fScore[neighbor] := gScore[neighbor] + heuristic_cost_estimate(neighbor, goal)"""