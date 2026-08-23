import random
import tkinter as tk

from agent import SearchAgent


class VisualGridHuntGame:

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=2,
        num_traps=3,
        custom_walls=None
    ):

        self.width = width
        self.height = height

        self.agent_pos = [0, 0]

        self.walls = (
            set(custom_walls)
            if custom_walls
            else {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}
        )

        # -------------------------
        # Create food
        # -------------------------
        self.food_positions = set()

        while len(self.food_positions) < num_food:

            pos = (
                random.randint(0, width - 1),
                random.randint(0, height - 1)
            )

            if pos != (0, 0) and pos not in self.walls:
                self.food_positions.add(pos)

        # -------------------------
        # Create toxic traps
        # -------------------------
        self.toxic_traps = set()

        while len(self.toxic_traps) < num_traps:

            pos = (
                random.randint(0, width - 1),
                random.randint(0, height - 1)
            )

            if (
                pos != (0, 0)
                and pos not in self.walls
                and pos not in self.food_positions
            ):
                self.toxic_traps.add(pos)

        # -------------------------
        # Create opponents
        # -------------------------
        self.opponents = []

        while len(self.opponents) < num_opponents:

            op = [
                random.randint(0, width - 1),
                random.randint(0, height - 1)
            ]

            if (
                tuple(op) != (0, 0)
                and tuple(op) not in self.walls
                and tuple(op) not in self.food_positions
            ):
                self.opponents.append(op)

        self.score = 0
        self.steps = 0
        self.collision = False

    # -------------------------
    # Percept
    # -------------------------
    def get_percept(self) -> dict:

        return {
            'agent_pos': list(self.agent_pos),
            'smells_toxin':
                tuple(self.agent_pos) in self.toxic_traps,
            'score': self.score,

            # Information needed by A*
            'remaining_food': set(self.food_positions),
            'walls': set(self.walls),
            'grid_size': (self.width, self.height)
        }

    # -------------------------
    # Execute Action
    # -------------------------
    def execute_action(self, action: str):

        self.steps += 1

        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(
                self.height - 1,
                new_pos[1] + 1
            )

        elif action == 'Down':
            new_pos[1] = max(
                0,
                new_pos[1] - 1
            )

        elif action == 'Left':
            new_pos[0] = max(
                0,
                new_pos[0] - 1
            )

        elif action == 'Right':
            new_pos[0] = min(
                self.width - 1,
                new_pos[0] + 1
            )

        # Wall check
        if tuple(new_pos) in self.walls:
            self.score -= 5

        else:
            self.agent_pos = new_pos

        # Food check
        if tuple(self.agent_pos) in self.food_positions:

            self.food_positions.remove(
                tuple(self.agent_pos)
            )

            self.score += 20

        # Toxic trap check
        if tuple(self.agent_pos) in self.toxic_traps:
            self.score -= 15

    # -------------------------
    # Check game end
    # -------------------------
    def is_done(self) -> bool:

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )


class GridGameGUI:

    def __init__(
        self,
        root,
        width=10,
        height=10,
        num_food=12,
        num_opponents=2,
        num_traps=3
    ):

        self.env = VisualGridHuntGame(
            width,
            height,
            num_food,
            num_opponents,
            num_traps
        )

        # -------------------------
        # Inject SearchAgent
        # -------------------------
        self.agent = SearchAgent()
        self.agent.active_algo = 'AStar'

        self.cell_size = 40

        self.canvas = tk.Canvas(
            root,
            width=width * 40,
            height=height * 40,
            bg="white"
        )

        self.canvas.pack()

        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0"
        )

        self.label.pack()

        self.draw_grid()

        # Start agent after 500ms
        root.after(500, self.run_agent)

    # -------------------------
    # Draw Game
    # -------------------------
    def draw_grid(self):

        self.canvas.delete("all")

        for x in range(self.env.width):

            for y in range(self.env.height):

                x1 = x * self.cell_size

                y1 = (
                    self.env.height - 1 - y
                ) * self.cell_size

                # Wall / normal cell
                if (x, y) in self.env.walls:
                    color = "#64748b"

                else:
                    color = "#f1f5f9"

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x1 + self.cell_size,
                    y1 + self.cell_size,
                    fill=color
                )

                # -------------------------
                # Food = Green
                # -------------------------
                if (x, y) in self.env.food_positions:

                    self.canvas.create_oval(
                        x1 + 12,
                        y1 + 12,
                        x1 + 28,
                        y1 + 28,
                        fill="green"
                    )

                # -------------------------
                # Toxic Trap = Purple
                # -------------------------
                if (x, y) in self.env.toxic_traps:

                    self.canvas.create_oval(
                        x1 + 10,
                        y1 + 10,
                        x1 + 30,
                        y1 + 30,
                        fill="purple"
                    )

        # -------------------------
        # Agent = Blue
        # -------------------------
        ax, ay = self.env.agent_pos

        self.canvas.create_oval(
            ax * self.cell_size + 5,
            (self.env.height - 1 - ay)
            * self.cell_size + 5,

            ax * self.cell_size + 35,
            (self.env.height - 1 - ay)
            * self.cell_size + 35,

            fill="blue"
        )

    # -------------------------
    # Agent Loop
    # -------------------------
    def run_agent(self):

        if self.env.is_done():

            self.label.config(
                text=
                f"Finished! Score: {self.env.score} "
                f"| Steps: {self.env.steps}"
            )

            return

        # Get environment information
        percept = self.env.get_percept()

        # A* agent chooses action
        action = self.agent.sense_and_act(
            percept
        )

        # Execute chosen action
        if action is not None:
            self.env.execute_action(action)

        # Update label
        self.label.config(
            text=
            f"Score: {self.env.score} "
            f"| Steps: {self.env.steps}"
        )

        # Redraw
        self.draw_grid()

        # Repeat every 300ms
        self.canvas.after(
            300,
            self.run_agent
        )


# -------------------------
# Start Program
# -------------------------
if __name__ == "__main__":

    root = tk.Tk()

    root.title(
        "A* Search - Visual Grid Game"
    )

    app = GridGameGUI(root)

    root.mainloop()