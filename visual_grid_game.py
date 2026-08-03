import random
import tkinter as tk


import random
import tkinter as tk


class ModelBasedAgent:
    def __init__(self):
        self.visited_cells = set()
        self.last_action = None
        self.position = (0, 0)

    def sense_and_act(self, percept):

        
        self.visited_cells.add(self.position)

        action = None

    
        if percept['wall_ahead'] and self.position in self.visited_cells:
            action = "Right"

        
        elif percept['smells_toxin']:
            action = "Left"

    
        elif percept['food_here']:
            action = "Up"

        
        else:
            action = "Up"

        
        self.last_action = action

        
        x, y = self.position

        if action == "Up":
            y += 1
        elif action == "Down":
            y -= 1
        elif action == "Left":
            x -= 1
        elif action == "Right":
            x += 1

        self.position = (x, y)

        return action

class VisualGridHuntGame:
    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, num_traps=3, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]
        self.facing = 'Up'
        self.walls = set(custom_walls) if custom_walls else {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}
        
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            pos = (random.randint(0, width - 1), random.randint(0, height - 1))
            if pos != (0, 0) and pos not in self.walls: self.food_positions.add(pos)
            
        self.toxic_traps = set()
        while len(self.toxic_traps) < num_traps:
            pos = (random.randint(0, width - 1), random.randint(0, height - 1))
            if pos != (0, 0) and pos not in self.walls and pos not in self.food_positions: self.toxic_traps.add(pos)
            
        self.opponents = []
        while len(self.opponents) < num_opponents:
            op = [random.randint(0, width - 1), random.randint(0, height - 1)]
            if tuple(op) != (0, 0) and tuple(op) not in self.walls and tuple(op) not in self.food_positions: self.opponents.append(op)
            
        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:
        next_x, next_y = self.agent_pos
        
        if self.facing == 'Up': next_y += 1
        elif self.facing == 'Down': next_y -= 1
        elif self.facing == 'Left': next_x -= 1
        elif self.facing == 'Right': next_x += 1

        wall_ahead = (next_x, next_y) in self.walls or next_x < 0 or next_x >= self.width or next_y < 0 or next_y >= self.height
        food_here = tuple(self.agent_pos) in self.food_positions

        return {
            'wall_ahead': wall_ahead,
            'food_here': food_here,
            'smells_toxin': tuple(self.agent_pos) in self.toxic_traps,
            'score': self.score
        }

    def execute_action(self, action: str):
        self.steps += 1
        
        if action in ['Up', 'Down', 'Left', 'Right']:
            self.facing = action
            
        new_pos = list(self.agent_pos)
        if action == 'Up': new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down': new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left': new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right': new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls: self.score -= 5
        else: self.agent_pos = new_pos

        if tuple(self.agent_pos) in self.food_positions:
            self.food_positions.remove(tuple(self.agent_pos))
            self.score += 20
        
        if tuple(self.agent_pos) in self.toxic_traps:
            self.score -= 15

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision

class GridGameGUI:
    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, num_traps=3):
        self.env = VisualGridHuntGame(width, height, num_food, num_opponents, num_traps)
        self.cell_size = 40
        self.canvas = tk.Canvas(root, width=width*40, height=height*40, bg="white")
        self.canvas.pack()
        self.label = tk.Label(root, text="Score: 0 | Steps: 0")
        self.label.pack()
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for x in range(self.env.width):
            for y in range(self.env.height):
                x1, y1 = x * self.cell_size, (self.env.height - 1 - y) * self.cell_size
                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x1+self.cell_size, y1+self.cell_size, fill=color)
                if (x, y) in self.env.toxic_traps:
                    self.canvas.create_oval(x1+10, y1+10, x1+30, y1+30, fill="purple")
 
        ax, ay = self.env.agent_pos
        self.canvas.create_oval(ax*self.cell_size+5, (self.env.height-1-ay)*self.cell_size+5, 
                                ax*self.cell_size+35, (self.env.height-1-ay)*self.cell_size+35, fill="blue")

if __name__ == "__main__":
    root = tk.Tk()
    app = GridGameGUI(root)
    root.mainloop()

    