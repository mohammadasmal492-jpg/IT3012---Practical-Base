# agent.py

import random
import math
import heapq


class GreedyGridAgent:
    """A simple agent that moves randomly."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)


class SearchAgent:

    def __init__(self):
        self.active_algo = 'AStar'
        self.plan = []

    # --------------------------------
    # Manhattan Distance
    # --------------------------------
    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    # --------------------------------
    # Euclidean Distance
    # --------------------------------
    def euclidean_distance(self, pos, goal):
        return math.sqrt(
            (pos[0] - goal[0]) ** 2 +
            (pos[1] - goal[1]) ** 2
        )

    # --------------------------------
    # A* Search
    # --------------------------------
    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan'
    ):

        start_pos = tuple(start_pos)
        goal_pos = tuple(goal_pos)

        priority_queue = []
        reached_states = set()

        if heuristic_type == 'euclidean':
            start_h = self.euclidean_distance(start_pos, goal_pos)
        else:
            start_h = self.manhattan_distance(start_pos, goal_pos)

        # (f_cost, g_cost, current_pos, path_taken)
        heapq.heappush(
            priority_queue,
            (start_h, 0, start_pos, [])
        )

        while priority_queue:

            f_cost, g_cost, current_pos, path_taken = heapq.heappop(
                priority_queue
            )

            if current_pos == goal_pos:
                return path_taken

            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            directions = [
                ((0, 1), 'Up'),
                ((0, -1), 'Down'),
                ((-1, 0), 'Left'),
                ((1, 0), 'Right')
            ]

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
                    and new_pos not in reached_states
                ):

                    new_g = g_cost + 1

                    if heuristic_type == 'euclidean':
                        new_h = self.euclidean_distance(
                            new_pos,
                            goal_pos
                        )
                    else:
                        new_h = self.manhattan_distance(
                            new_pos,
                            goal_pos
                        )

                    new_f = new_g + new_h

                    heapq.heappush(
                        priority_queue,
                        (
                            new_f,
                            new_g,
                            new_pos,
                            path_taken + [action]
                        )
                    )

        return []

    # --------------------------------
    # Agent Decision Loop
    # --------------------------------
    def sense_and_act(self, percept):

        if self.active_algo == 'AStar':

            current_pos = tuple(percept['agent_pos'])
            remaining_food = percept['remaining_food']
            walls = percept['walls']
            grid_size = percept['grid_size']

            if not remaining_food:
                return None

            # If current plan finished, find another food
            if not self.plan:

                goal_pos = min(
                    remaining_food,
                    key=lambda food:
                    self.manhattan_distance(
                        current_pos,
                        food
                    )
                )

                self.plan = self.astar_search(
                    current_pos,
                    goal_pos,
                    walls,
                    grid_size,
                    heuristic_type='manhattan'
                )

            if self.plan:
                return self.plan.pop(0)

        return None


# --------------------------------
# Testing Checkpoint
# --------------------------------
if __name__ == "__main__":

    agent = SearchAgent()

    print(
        "Manhattan:",
        agent.manhattan_distance((0, 0), (3, 4))
    )

    print(
        "Euclidean:",
        agent.euclidean_distance((0, 0), (3, 4))
    )