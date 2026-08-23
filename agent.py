# agent.py

import random
import heapq
from collections import deque


class GreedyGridAgent:
    """Original simple random agent."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)


class SearchAgent:

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'

    # --------------------------------
    # Manhattan distance
    # Used only to choose closest food
    # --------------------------------
    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    # --------------------------------
    # Get valid neighbouring cells
    # --------------------------------
    def get_neighbors(self, current_pos, walls, grid_size):

        directions = [
            ((0, 1), 'Up'),
            ((0, -1), 'Down'),
            ((-1, 0), 'Left'),
            ((1, 0), 'Right')
        ]

        neighbors = []

        for (dx, dy), action in directions:

            new_pos = (
                current_pos[0] + dx,
                current_pos[1] + dy
            )

            x, y = new_pos

            if (
                0 <= x < grid_size[0]
                and 0 <= y < grid_size[1]
                and new_pos not in walls
            ):
                neighbors.append((new_pos, action))

        return neighbors

    # ==============================================
    # BFS - Breadth First Search
    # FIFO Queue
    # ==============================================
    def bfs_search(self, start_pos, goal_pos, walls, grid_size):

        start_pos = tuple(start_pos)
        goal_pos = tuple(goal_pos)
        walls = set(walls)

        frontier = deque()

        frontier.append(
            (start_pos, [])
        )

        reached = set()
        reached.add(start_pos)

        while frontier:

            current_pos, path = frontier.popleft()

            if current_pos == goal_pos:
                return path

            for new_pos, action in self.get_neighbors(
                current_pos,
                walls,
                grid_size
            ):

                if new_pos not in reached:

                    reached.add(new_pos)

                    frontier.append(
                        (
                            new_pos,
                            path + [action]
                        )
                    )

        return []

    # ==============================================
    # DFS - Depth First Search
    # LIFO Stack
    # ==============================================
    def dfs_search(self, start_pos, goal_pos, walls, grid_size):

        start_pos = tuple(start_pos)
        goal_pos = tuple(goal_pos)
        walls = set(walls)

        frontier = []

        frontier.append(
            (start_pos, [])
        )

        reached = set()

        while frontier:

            current_pos, path = frontier.pop()

            if current_pos == goal_pos:
                return path

            if current_pos in reached:
                continue

            reached.add(current_pos)

            for new_pos, action in self.get_neighbors(
                current_pos,
                walls,
                grid_size
            ):

                if new_pos not in reached:

                    frontier.append(
                        (
                            new_pos,
                            path + [action]
                        )
                    )

        return []

    # ==============================================
    # UCS - Uniform Cost Search
    # Priority Queue based on g(n)
    # ==============================================
    def ucs_search(self, start_pos, goal_pos, walls, grid_size):

        start_pos = tuple(start_pos)
        goal_pos = tuple(goal_pos)
        walls = set(walls)

        frontier = []

        # (cost, current_position, path)
        heapq.heappush(
            frontier,
            (0, start_pos, [])
        )

        reached = set()

        while frontier:

            cost, current_pos, path = heapq.heappop(
                frontier
            )

            if current_pos == goal_pos:
                return path

            if current_pos in reached:
                continue

            reached.add(current_pos)

            for new_pos, action in self.get_neighbors(
                current_pos,
                walls,
                grid_size
            ):

                if new_pos not in reached:

                    new_cost = cost + 1

                    heapq.heappush(
                        frontier,
                        (
                            new_cost,
                            new_pos,
                            path + [action]
                        )
                    )

        return []

    # ==============================================
    # Agent decision loop
    # ==============================================
    def sense_and_act(self, percept):

        current_pos = tuple(percept['agent_pos'])
        all_food = percept['all_food']
        walls = percept['walls']
        grid_size = percept['grid_size']

        if not all_food:
            return None

        # Create a new plan only when old plan is empty
        if not self.plan:

            # Find closest food
            goal_pos = min(
                all_food,
                key=lambda food:
                    self.manhattan_distance(
                        current_pos,
                        food
                    )
            )

            # Select search algorithm
            if self.active_algo == 'BFS':

                self.plan = self.bfs_search(
                    current_pos,
                    goal_pos,
                    walls,
                    grid_size
                )

            elif self.active_algo == 'DFS':

                self.plan = self.dfs_search(
                    current_pos,
                    goal_pos,
                    walls,
                    grid_size
                )

            elif self.active_algo == 'UCS':

                self.plan = self.ucs_search(
                    current_pos,
                    goal_pos,
                    walls,
                    grid_size
                )

        # Execute first action in plan
        if self.plan:
            return self.plan.pop(0)

        return None


# --------------------------------
# Simple testing
# --------------------------------
if __name__ == "__main__":

    agent = SearchAgent()

    start = (0, 0)
    goal = (3, 4)
    walls = set()
    grid_size = (10, 10)

    print(
        "BFS Path:",
        agent.bfs_search(
            start,
            goal,
            walls,
            grid_size
        )
    )

    print(
        "DFS Path:",
        agent.dfs_search(
            start,
            goal,
            walls,
            grid_size
        )
    )

    print(
        "UCS Path:",
        agent.ucs_search(
            start,
            goal,
            walls,
            grid_size
        )
    )