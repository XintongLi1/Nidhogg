from collections import deque
import json

INT_MIN, INT_MAX = -10 ** 3, 10 ** 3


class Preprocessing:
    def __init__(self, board, me):  # board = data["board"], me = data["me"]
        self.me = me
        self.height = board["height"]
        self.width = board["width"]
        self.food = board["food"]
        self.snakes = board["snakes"]
        # self.hazards = board["hazards"]
        self.board = self.init_board()

        self.distance = [[-1] * self.width for _ in range(self.height)]
        """
        Distance[y][x] is the distance between "my head" to the grid (x, y)
        Distance[y][x] = -1 means unreachable
        Call get_distance() to fill self.distance with information
        """
        self.direction = [[None] * self.width for _ in range(self.height)]  # "up" or "down" or "left" or "right"
        # Updated along with self.distance

        self.weights = [[0] * self.width for _ in range(self.height)]
        """
        self.weights can be modified by get_weights(), avoid_corners(), avoid_snakes(), attack_rivals() and detect_food()
        """

    def init_board(self):
        """
        We use number to denote different items on the board.
        0 for empty, 1 for (mine and rival snakes') body, 2 for rivals' head, 3 for my head, 4 for food

        The Y-Axis is positive in the up direction, and X-Axis is positive to the right
        """
        board = [[0] * self.width for _ in range(self.height)]
        for snake in self.snakes:
            # Snake's tail will be freed in the next move
            for body in snake["body"][:-1]:
                board[body["y"]][body["x"]] = 1
            head = snake["head"]
            board[head["y"]][head["x"]] = 2
        head = self.me["head"]
        board[head["y"]][head["x"]] = 3
        for food in self.food:
            board[food["y"]][food["x"]] = 4

        return board

    def get_neighbors(self, y, x, ordered_directions=None):
        if ordered_directions is None:
            ordered_directions = ['up', 'down', 'left', 'right']
        coordinates = {
            'up': {'x': 0, 'y': 1},
            'down': {'x': 0, 'y': -1},
            'left': {'x': -1, 'y': 0},
            'right': {'x': 1, 'y': 0},
        }
        neighbors = []
        for direction in ordered_directions:
            Y = y + coordinates[direction]['y']
            X = x + coordinates[direction]['x']
            if 0 <= Y < self.height and 0 <= X < self.width:
                neighbors.append((direction, Y, X))
        return neighbors

    def get_distance(self, y, x, ordered_directions=None):
        # Strategy: BFS, FloodFill
        self.distance = [[-1] * self.width for _ in range(self.height)]
        self.direction = [[None] * self.width for _ in range(self.height)]
        space = 0
        if ordered_directions is None:
            ordered_directions = ['up', 'down', 'left', 'right']
        self.distance[y][x] = 0
        queue = deque()
        for direction, ny, nx in self.get_neighbors(y, x, ordered_directions):
            self.distance[ny][nx] = 1
            self.direction[ny][nx] = direction
            if self.board[ny][nx] == 0 or self.board[ny][nx] == 4:
                queue.append((ny, nx))
        while queue:
            y, x = queue.popleft()
            space += 1
            for _, ny, nx in self.get_neighbors(y, x, ordered_directions):
                if self.distance[ny][nx] == -1:
                    self.distance[ny][nx] = self.distance[y][x] + 1
                    self.direction[ny][nx] = self.direction[y][x]
                    if self.board[ny][nx] == 0 or self.board[ny][nx] == 4:
                        queue.append((ny, nx))
        return space

    def closest_food(self, allowed_direction=None):
        if allowed_direction is None:
            allowed_direction = []
        ordered_directions = allowed_direction + [i for i in ['up', 'down', 'left', 'right'] if
                                                  i not in allowed_direction]
        self.get_distance(y=self.me["head"]["y"], x=self.me["head"]["x"], ordered_directions=ordered_directions)
        distance = 122
        y, x = None, None
        for food in self.food:
            if -1 < self.distance[food['y']][food['x']] <= distance and \
                    self.direction[food['y']][food['x']] in allowed_direction:
                print("closest_food:", (y, x), self.distance[y][x])
                if self.distance[food['y']][food['x']] == distance:
                    if type(y) is int:
                        y, x = [y] + [food['y']], [x] + [food['x']]
                    else:
                        y, x = list(y) + [food['y']], list(x) + [food['x']]
                else:
                    distance = self.distance[food['y']][food['x']]
                    y, x = food['y'], food['x']
        return list(zip(y, x)) if type(y) is list else [(y, x)]

    def avoid_corners(self):
        # Add weights to area around walls. Assign heavy weight to corners
        corner_weights = [[7, 5, 4, 3], [5, 4, 3, 2], [4, 3, 2, 1]]
        for i in range(3):
            for j in range(self.width):
                self.weights[i][j] = max(self.weights[i][j], corner_weights[i][min(3, j)])
                self.weights[i][self.width - 1 - j] = max(self.weights[i][self.width - 1 - j],
                                                          corner_weights[i][min(3, j)])
                self.weights[self.height - 1 - i][j] = max(self.weights[self.height - 1 - i][j],
                                                           corner_weights[i][min(3, j)])
                self.weights[self.height - 1 - i][self.width - 1 - j] = max(
                    self.weights[self.height - 1 - i][self.width - 1 - j],
                    corner_weights[i][min(3, j)])
        for i in range(3):
            for j in range(self.height):
                self.weights[j][i] = max(self.weights[j][i], corner_weights[i][min(3, j)])
                self.weights[j][self.width - 1 - i] = max(self.weights[j][self.width - 1 - i],
                                                          corner_weights[i][min(3, j)])
                self.weights[self.height - 1 - j][i] = max(self.weights[self.height - 1 - j][i],
                                                           corner_weights[i][min(3, j)])
                self.weights[self.height - 1 - j][self.width - 1 - i] = max(
                    self.weights[self.height - 1 - j][self.width - 1 - i],
                    corner_weights[i][min(3, j)])

    def avoid_snakes(self):
        snake_weights = [[0] * self.width for _ in range(self.height)]
        queue = deque()
        last, level, flag = None, 0, 0
        for snake in self.snakes:
            if snake["head"] != self.me["head"] and snake["length"] >= self.me["length"]:
                snake_next_move = self.get_neighbors(snake["head"]['y'], snake["head"]['x'])
                for _, y, x in snake_next_move:  # area around head is the most dangerous
                    snake_weights[y][x] += 4
            for body in snake["body"][:-1]:
                queue.append((0, body['y'], body['x']))
                last = (body['y'], body['x'])

        while queue and level < 2 and not flag:
            level, y, x = queue.popleft()
            flag = ((y, x) == last)
            for _, ny, nx in self.get_neighbors(y, x, ['up', 'left']):
                snake_weights[ny][nx] += max(2 - level, 0)
                if flag == 1:
                    last = (ny, nx)
                    flag = 0
                if self.weights[ny][nx] < INT_MAX: queue.append((level + 1, ny, nx))

        queue = deque()
        last, level, flag = None, 0, 0
        for snake in self.snakes:
            for body in snake["body"][:-1]:
                queue.append((0, body['y'], body['x']))
                last = (body['y'], body['x'])

        while queue and level < 2 and not flag:
            level, y, x = queue.popleft()
            flag = ((y, x) == last)
            for _, ny, nx in self.get_neighbors(y, x, ['down', 'right']):
                snake_weights[ny][nx] += max(2 - level, 0)
                if flag == 1:
                    last = (ny, nx)
                    flag = 0
                if self.weights[ny][nx] < INT_MAX: queue.append((level + 1, ny, nx))

        for i in range(self.height):
            for j in range(self.width):
                self.weights[i][j] = self.weights[i][j] + float("{:.2f}".format(snake_weights[i][j])) \
                    if self.weights[i][j] < INT_MAX else self.weights[i][j]

    def detect_food(self, coef):
        unit_weight = -6.4 * coef
        food_weights = [[0] * self.width for _ in range(self.height)]
        last, level, flag = None, 0, 0
        queue = deque()
        for food in self.food:
            y, x = food['y'], food['x']
            if self.me["health"] > 6:  # when not desperate for food
                rival_goal = self.get_neighbors(y, x)
                for _, ny, nx in rival_goal:  # if the food is reachable by a rival in one move, then ignore it
                    if self.board[ny][nx] == 2:
                        flag = 1
            if not flag:
                last = (y, x)
                queue.append((0, y, x))
                food_weights[y][x] = min(unit_weight, food_weights[y][x])
            flag = 0
        while queue and level < 4 and not flag:
            level, y, x = queue.popleft()
            flag = ((y, x) == last)
            for _, ny, nx in self.get_neighbors(y, x):
                if unit_weight + (level * 1.6 + 2.4) < food_weights[ny][nx]:
                    food_weights[ny][nx] = unit_weight + (level * 1.6 + 2.4)
                    queue.append((level + 1, ny, nx))
                    if flag == 1:
                        last = (ny, nx)
                        flag = 0
        for i in range(self.height):
            for j in range(self.width):
                self.weights[i][j] = float("{:.1f}".format(self.weights[i][j] + food_weights[i][j])) \
                    if self.weights[i][j] < INT_MAX else self.weights[i][j]

    def attack_rivals(self):  # attack and defend
        pass

    def get_weights(self):
        """
        Passive/Defensive Strategy:
            1. Must call avoid_corners() first
            2. Call avoid_snakes()
            3. Call detect_food()
            4. Call attack_rivals()

        """
        for i in range(self.height):
            for j in range(self.width):
                if 1 <= self.board[i][j] <= 3:
                    self.weights[i][j] = INT_MAX

        self.avoid_corners()
        self.avoid_snakes()

        health = [12, 36, 100]
        coefficients = [1.6, 1.2, 1]
        food_coef = 1
        for i in range(8):
            if self.me["health"] <= health[i]:
                food_coef = coefficients[i]
                break
        for snake in self.snakes:
            if snake["id"] != self.me["id"] and snake["health"] >= self.me["health"]:
                food_coef = 1.6
                break
        self.detect_food(food_coef)

        # self.attack_rivals()

    def get_shortest_path(self, level=5):
        """
        Can only be called after self.get_weights() is called
        Modify self.distance -> shortest weight in the path from head to (x, y)
        :param level:
        :return:
        """
        y, x = self.me["head"]['y'], self.me["head"]['x']
        path = []
        shortest_weight, best_direction, weight = INT_MAX, None, INT_MAX
        for direction, ny, nx in self.get_neighbors(y, x):
            if self.weights[ny][nx] < INT_MAX:
                shortest_path_weight, tmp_visited = self.DFS(ny, nx, level - 1, [(self.weights[y][x], y, x),
                                                                                 (self.weights[ny][nx], ny, nx)])
                if len(tmp_visited) >= len(path) and \
                        (shortest_path_weight + self.weights[ny][nx] < shortest_weight or
                         (shortest_path_weight + self.weights[ny][nx] == shortest_weight and self.weights[ny][nx] < weight) or
                         len(tmp_visited) > len(path)):
                    best_direction = direction
                    shortest_weight = shortest_path_weight + self.weights[ny][nx]
                    weight = self.weights[ny][nx]
                    path = tmp_visited
                self.distance[ny][nx] = shortest_path_weight + self.weights[ny][nx]
        path[0] = ('Start', y, x)
        return best_direction, shortest_weight, path

    def DFS(self, y, x, level, visited: list):
        if level == 0:
            return 0, visited
        shortest_weight, weight, path = INT_MAX, INT_MAX, []
        for _, ny, nx in self.get_neighbors(y, x):
            if (self.weights[ny][nx], ny, nx) not in visited and self.weights[ny][nx] < INT_MAX:
                shortest_path_weight, tmp_visited = self.DFS(ny, nx, level - 1,
                                                             visited + [(self.weights[ny][nx], ny, nx)])
                if len(tmp_visited) >= len(path) and \
                        (shortest_path_weight + self.weights[ny][nx] < shortest_weight or
                         (shortest_path_weight + self.weights[ny][nx] == shortest_weight and self.weights[ny][nx] < weight) or
                         len(tmp_visited) > len(path)):
                    shortest_weight = shortest_path_weight + self.weights[ny][nx]
                    weight = self.weights[ny][nx]
                    path = tmp_visited
                self.distance[ny][nx] = shortest_path_weight + self.weights[ny][nx]
        if not path:
            return 0, visited
        return shortest_weight, path
