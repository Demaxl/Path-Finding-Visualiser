import time, threading
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror

class Node:
    """A class that represent the node
       a node contains:
       - a state
       - a parent
       - action
        """
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

class StackFrontier:
    """ A class that represents the frontier using Depth-First Search"""
    def __init__(self):
        # Frontier list
        self.frontier = []
    
    def add(self, node):
        """ Adds a node to the frontier """
        self.frontier.append(node)
    
    def contains_state(self, state):
        """ Checks if the frontier has a particular state"""
        return any([node.state == state for node in self.frontier])
    
    def empty(self):
        """ Check if the frontier is empty"""
        return len(self.frontier) == 0
    
    def remove(self):
        """ Removes the last node in the frontier (LIFO)"""
        if self.empty():
            raise Exception("empty frontier")
        else:
            return self.frontier.pop()

class QueueFrontier(StackFrontier):
    """ Class that represents the frontier using Breadth-First Search"""
    def __init__(self):
        super().__init__()
    
    def remove(self):
        if self.empty():
            raise Exception("Empty Frontier")
        else:
            # Queue
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class GreedyFrontier(StackFrontier):
    """ Class that represents the frontier using Greedy Best-First Search"""
    def __init__(self, goal):
        self.goal = goal
        super().__init__()
    
    def heuristic(self, state):
        """ Heuristic function, h(n) for greedy algorithm 
            Calculate which square is closest to the goal"""
        x = state
        y = self.goal

        steps = 0
        x_direction = -1 if x[0] > y[0] else 1
        y_direction = 1 if x[1] < y[1] else -1

        for _ in range(x[0], y[0], x_direction):
            steps += 1
        for _ in range(x[1], y[1], y_direction):
            steps += 1
        
        return steps 
    
    def remove(self):
        distances = {}
    
        for i, neighbour in enumerate(self.frontier):
            dist = self.heuristic(neighbour.state)
            distances[neighbour] = dist

        shortest = min(distances.values())

        for node, distance in distances.items():
            if distance == shortest:
                chosen = node       
                self.frontier.remove(chosen)
                return chosen

class AStar(GreedyFrontier):
    def __init__(self, goal):
        super().__init__(goal)
    
    def g(self, node):
        steps = 0

        while node.parent is not None:
            steps += 1

            node = node.parent
        
        return steps

    def remove(self):
        distances = {}

        for i, neighbour in enumerate(self.frontier):
            h = self.heuristic(neighbour.state)
            g = self.g(neighbour)
            distances[neighbour] = g + h

        shortest = min(distances.values())

        for node, distance in distances.items():
            if distance == shortest:
                chosen = node       
                self.frontier.remove(chosen)
                return chosen

class Maze:
    def __init__(self, board, master):
        self.board = board
        self.master = master

        self.canvas = Canvas(width=1000, height=600)
        self.states_label = Label(self.master, text='', font="Courier 20")
        self.status_label = Label(self.master, text='', font="Courier 20")

        self.algo = StringVar()
        self.algo.set('A* Search')

        self.algotable = {
            'Depth First Search': 'DFS',
            'Breadth First Search': 'BFS',
            'Greedy Best First': 'GBFS',
            'A* Search': 'ASTAR'}

        algobox = ttk.Combobox(self.master, state='readonly', font='Courier 20', textvariable=self.algo, width=20)
        algobox['values'] = list(self.algotable.keys())


        Label(text='Search Algorithm:', font='Courier 20').place(x=20, y=0)                      
        algobox.pack()   
        self.canvas.pack()
        self.states_label.pack()
        self.status_label.pack()
        
        SIZE = 20

        x1 = 0; y1 = 0

        for r in range(30):
            for c in range(50):
                color = 'black'

                if (r, c) == (15, 10):
                    color = 'green'
                    self.start = (r, c)
                elif (r, c) == (15, 35):
                    color = 'red'
                    self.goal = (r, c)

                board[r][c] = self.canvas.create_rectangle(x1, y1, x1 + SIZE, y1 + SIZE, fill=color, outline='gray')

                x1 += SIZE
                
            y1 += SIZE
            x1 = 0

        self.dragging = False
        self.place_start = False
        self.place_goal = False
        self.animating = False
        self.erasing = False
        self.terminate = False
        self.clearable = True

        
        self.canvas.bind('<Button-1>', self.click_event)
        self.canvas.bind('<Button-3>', self.right_click_event)
        self.canvas.bind('<Motion>', self.drag_event)
        self.master.bind('<Key>', self.initiate)

        self.canvas.focus_set()
        threading.Thread(target=self.update_status).start()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        self.terminate = True
        self.master.destroy()

    def click_event(self, event):
        if self.animating:
            return

        if self.erasing: return

        box = self.canvas.gettags("current")[0]
        color = self.canvas.itemcget(box, 'fill')

        if self.place_start: 
            if color == 'red': return
            self.canvas.itemconfigure(box, fill='green')
            self.place_start = False

        elif self.place_goal:
            if color == 'green': return
            self.canvas.itemconfigure(box, fill='red')
            self.place_goal = False
        else:
            if color == 'green':
                self.place_start = True
                self.dragging = False
                self.canvas.itemconfigure(box, fill='black')
            elif color == 'red':
                self.place_goal = True
                self.dragging = False
                self.canvas.itemconfigure(box, fill='black')
            else:
                self.dragging = True if not self.dragging else False

    def right_click_event(self, event):
        if self.animating:
            return
        if not self.dragging:
            self.erasing = True if not self.erasing else False

    def drag_event(self, event):
        if self.dragging or self.erasing:
            try:
                box = self.canvas.gettags("current")[0]
                color = self.canvas.itemcget(box, 'fill')
                
                # Not start or end
                if (color != 'red') and (color != 'green'):
                    new_fill = 'white' if not self.erasing else 'black'
                    self.canvas.itemconfigure(box, fill=new_fill)
            except IndexError:
                pass
    
    def release(self, event):
        self.dragging = False
    

    def update_status(self):
        while not self.terminate :
            # if not self.animating:
                text = ''
                if self.dragging:
                    text = 'Drawing Obstacles'
                elif self.place_start:
                    text = 'Choosing Start position'
                elif self.place_goal:
                    text = 'Choosing goal position'
                elif self.erasing:
                    text = 'Erasing obstacles'
                
                self.status_label.configure(text=text)
                self.master.update()

    def neighbors(self, state):
        row, col = state # 5, 1

        directions = {
            "up": (row-1, col),
            "down": (row+1, col),
            "left": (row, col-1),
            "right": (row, col+1)
        }
        results = []

        for direction, pos in directions.items():
            try:
                r, c = pos
                if (r < 0) or (c < 0):
                    continue
                if self.canvas.itemcget(self.board[r][c], 'fill') != 'white':
                    results.append((direction, pos))
            except IndexError:
                pass    
        return results

    def show_explored(self):
        self.animating = True
        self.clearable = False
        self.status_label.configure(text='Finding Path..')
        for r, c in self.explored_list[1:]:
            if (r, c) != self.start or (r, c) != self.goal:
                self.canvas.itemconfigure(self.board[r][c], fill='pink')
                time.sleep(0.00001)
                self.master.update()
                self.master.update_idletasks()


    def show_solution(self, cells):
        self.clearable = False
        for r, c in cells:
            if (r, c) != self.start and (r, c) != self.goal:
                self.canvas.itemconfigure(self.board[r][c], fill='yellow')
                time.sleep(0.01)
                self.master.update()
                self.master.update_idletasks()
        self.clearable = True

        print(f"States Explored: {self.num_explored}")
        self.states_label.configure(text=f"States Explored: {self.num_explored}")
        self.status_label.configure(text='Found path!')

    def clear_board(self):
        for r in range(30):
            for c in range(50):
                box = self.board[r][c]
                color = self.canvas.itemcget(box, 'fill')

                if color != 'red' and color != 'green':
                    self.canvas.itemconfigure(box, fill='black')
                
        self.animating = False
    
    def solve(self, algo):
        self.num_explored = 0
        if algo == 'DFS':
            # Depth-First Search Algorithm
            frontier = StackFrontier()
        elif algo == 'BFS':
            # Breadth-First Search Algorithm
            frontier = QueueFrontier()
        elif algo == 'GBFS':
            # Greedy Best-First Search Algorithm
            frontier = GreedyFrontier(self.goal)
        elif algo == 'ASTAR':
            # A* path finding Algorithm
            frontier = AStar(self.goal)

        frontier.add(Node(self.start, parent=None, action=None))

        self.explored = set()
        self.explored_list = []


        while True:
            if frontier.empty():
                showerror(title='No path', message="No solution to this maze")
                self.clear_board()
                return

            node = frontier.remove()
            self.num_explored += 1

            if node.state == self.goal:
                actions = []
                cells = []

                while node.parent is not None:
                    cells.append(node.state)
                    actions.append(node.action)

                    node = node.parent

                actions.reverse()
                cells.reverse()
                self.show_explored()
                self.show_solution(cells)

                return
            
            self.explored.add(node.state)
            self.explored_list.append(node.state)


            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:

                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)


    def initiate(self, event):
        if event.keysym == 'BackSpace':
            if self.clearable:
                self.clear_board()
            return
        elif event.keysym != 'space':
            return

        if self.animating: return
        self.dragging = False
        for r in range(30):
            for c in range(50):
                box_color = self.canvas.itemcget(self.board[r][c], 'fill')
                if box_color == 'green':
                    self.start = (r, c)
                    
                elif box_color == 'red':
                    self.goal = (r, c)
                    


        algo = self.algotable[self.algo.get()]
        self.solve(algo)

        



    
board = [[c for c in range(50)] for r in range(30)]

root = Tk()
root.minsize(1000, 600)
root.title('Path Finding Visualizer')

maze = Maze(board, root)

root.mainloop()




