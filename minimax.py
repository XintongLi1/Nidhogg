"""
Implementing Minimax Algorithm
    - while applying Alpha-Beta Pruning for optimization
"""

from preprocessing import Preprocessing
import random
from math import inf

"""
Heuristics:
1. Assign infinite scores to dead position or health = 0
2. High score to the direction that causes the death of a rival
3. High score to open area (space = get_distance(my_position))
4. High score if me.health = max(rival.health) + 1
5. Weighted score based on the distance to the food
6. If same score, choose the closest position to the center of the board
"""
created_lookup = False
zobrist_lookup_table = []

class Minimax:
    def __init__(self, board, me):  # board = data["board"], me = data["me"]
        global zobrist_lookup_table, created_lookup
        self.start = Preprocessing(board, me)
        """
        Zobrist Hashing algorithm
            state: object / length (if applicable)
            index:
                0       empty 
                1       body
                2       food
                3-63    my head       2 + length
                64-124  rival's head  63 + length      
                               
        """
        if not created_lookup:
            zobrist_lookup_table = [[[0] + [random.randint(1, 2**64 - 1) for _ in range(124)] for _ in range(self.start.width)] for _ in range(self.start.height)]
            created_lookup = True
        self.zobrist_lookup = zobrist_lookup_table
        self.states = [[] for _ in range(2**16)]

    def zobristHash(self, board=None):
        if board is None:
            board = self.start.board
        hash_value = 0
        for i in range(self.start.height):
            for j in range(self.start.width):
                if board[i][j]:
                    obj = 0
                    if board[i][j] == 1:
                        obj = 1
                    elif board[i][j] == 4:
                        obj = 2
                    hash_value ^= self.zobrist_lookup[i][j][obj]
        for snake in self.start.snakes:
            if snake["id"] == self.start.me["id"]:
                hash_value ^= self.zobrist_lookup[snake["head"]['y']][snake["head"]['x']][2 + snake["length"]]
            else:
                hash_value ^= self.zobrist_lookup[snake["head"]['y']][snake["head"]['x']][63 + snake["length"]]
        return hash_value

    def add_to_hash_table(self, hash_value):
        index = hash_value & 0xFFFF
        if not self.in_hashtable(hash_value, index):
            self.states[index].append(hash_value)

    def in_hashtable(self, hash_value, index=None):
        if index is None:
            index = hash_value & 0xFFFF
        for hv in self.states[index]:
            if hv == hash_value:
                return True
        return False

    def update_state_hash_value(self, hash_value, snake, to_position_y, to_position_x):
        zobrist_type = 2 + snake["length"] if snake["id"] == self.start.me["id"] else 63 + snake["length"]
        hash_value ^= self.zobrist_lookup[snake.head['y']][snake.head['x']][zobrist_type]  # head away
        hash_value ^= self.zobrist_lookup[to_position_y][to_position_x][zobrist_type]  # head to
        hash_value ^= self.zobrist_lookup[snake["body"][-2]['y']][snake["body"][-2]['x']][1]  # tail away
        # remove hash_value for object at to_position
        if self.start.board[to_position_y][to_position_x] == 1:
            hash_value ^= self.zobrist_lookup[to_position_y][to_position_x][1]
        elif self.start.board[to_position_y][to_position_x] == 4:
            hash_value ^= self.zobrist_lookup[to_position_y][to_position_x][4]
        elif self.start.board[to_position_y][to_position_x] in [2, 3]:
            for snake in self.start.snakes:
                if snake["head"]['y'] == to_position_y and snake["head"]['x'] == to_position_x:
                    if snake["id"] == self.start.me["id"]:
                        hash_value ^= self.zobrist_lookup[to_position_y][to_position_x][2 + snake["length"]]
                    else:
                        hash_value ^= self.zobrist_lookup[to_position_y][to_position_x][63 + snake["length"]]
        return hash_value

    def get_score(self, state_board):
        pass

    def minimax(self, state_board, state_hash_value, depth, player, alpha, beta):
        pass

    def best_move(self):
        best_score = inf
        