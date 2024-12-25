import random
import matplotlib.pyplot as plt
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkscrolledframe import ScrolledFrame

with open ('cats_name.TXT', 'r', encoding='utf-8') as f:
    cats_names = f.read().splitlines()

class Cats_first_gen:
    def __init__(self, name, color): # конструктор
        self.name = name # имя
        self.color = {color:100}  # цвет
        self.age = 1 # возраст

class Cats_second_gen:
    def __init__(self, name, parent1, parent2):
        self.name = name
        self.color1 = parent1.color
        self.color2 = parent2.color
        self.new_color_func()
        self.age = 1
        parent1.age += 1
        parent2.age += 1

    def new_color_func(self):
        all_unique_colors = set(self.color1.keys()) | set(self.color2.keys())
        color_dict = {}
        for color in all_unique_colors:
            color_dict[color] = 0
        for color, percent in self.color1.items():
            color_dict[color] += percent
        for color, percent in self.color2.items():
            color_dict[color] += percent
        color_dict = {k: v for k, v in sorted(color_dict.items(), key=lambda item: item[1], reverse=True)}
        new_color = {}
        hundred = 100
        for color, percent in color_dict.items():
            if hundred >0:
                if percent > hundred:
                    percent = hundred
                new_color[color] = random.randint(0, percent)
                hundred -= new_color[color]
        if hundred > 0:
            for i in reversed(list(new_color.keys())):
                if new_color[i] + hundred < color_dict[i]:
                    new_color[i] += hundred
                    break
        new_color = {k: v for k, v in sorted(new_color.items(), key=lambda item: item[1], reverse=True)}
        self.color = new_color
        self.string_color = ''
        for key, value in new_color.items():
             self.string_color += str(value) + '% ' + key + ' '
        return self.color

def choose_parents(parents):
    parent1 = random.choice(parents)
    parent2 = random.choice(parents)
    while parent1 == parent2:
        parent2 = random.choice(parents)
    return parent1, parent2

def chose_name():
    name = random.choice(cats_names)
    cats_names.remove(name)
    name = name.split(' ')[1]
    return name

cats_colors = ['red', 'blue', 'green', 'yellow', 'black', 'orange', 'pink', 'purple', 'brown', 'grey','lime', 'cyan', 'magenta', 'olive', 'teal', 'navy', 'maroon','fuchsia']

def chose_color():
    color = random.choice(cats_colors)
    cats_colors.remove(color)
    return color

class vizual:
    def __init__(self,cats_colors, cats_names):
        self.cats_colors = cats_colors
        self.cats_names = cats_names
        self.parents = []
        self.childs = []
        self.childs2 = []
        self.childs3 = []
        for i in range(6):
            self.parents.append(Cats_first_gen(chose_name(), chose_color()))            
        for i in range(random.randint(4, 6)):
            parent1, parent2 = choose_parents(self.parents)
            self.childs.append(Cats_second_gen(chose_name(), parent1, parent2))
        for i in range(random.randint(4, 6)):
            parent1, parent2 = choose_parents(self.childs)
            self.childs2.append(Cats_second_gen(chose_name(), parent1, parent2))
        for i in range(random.randint(4, 6)):
            parent1, parent2 = choose_parents(self.childs2)
            self.childs3.append(Cats_second_gen(chose_name(), parent1, parent2))

    def vizual_window(self):
        self.frame_main = Frame()
        self.frame_main.pack()

        self.sf = ScrolledFrame(self.frame_main,width=1500, height=800)
        self.sf.pack(fill="both", expand=True)
        self.sf.bind_arrow_keys(self.frame_main)
        self.sf.bind_scroll_wheel(self.frame_main)
        self.frame = self.sf.display_widget(Frame)
        self.inner_frame = self.sf.display_widget(Frame)

        self.frame.pack(fill="both", expand=True)
        self.frame_parents = Frame(self.inner_frame)
        self.frame_parents.pack()
        self.frame_childs1 = Frame(self.inner_frame)
        self.frame_childs1.pack()
        self.frame_childs2 = Frame(self.inner_frame)
        self.frame_childs2.pack()
        self.frame_childs3 = Frame(self.inner_frame)
        self.frame_childs3.pack()

        self.frame_dict = {0:[self.parents,self.frame_parents],
                           1:[self.childs,self.frame_childs1],
                           2:[self.childs2,self.frame_childs2],
                           3:[self.childs3,self.frame_childs3]}

        for i in range(0,4):
            for j in self.frame_dict[i][0]:
                self.figure = plt.figure(figsize=(2, 2), dpi=100)
                self.ax = self.figure.add_subplot(111)
                self.ax.pie(j.color.values(), colors = list(j.color.keys()))
                self.ax.set_title(j.name)
                self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame_dict[i][1])
                self.canvas.draw()
                self.canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=1)

if __name__ == "__main__":
    root = Tk()
    example = vizual(cats_colors, cats_names)
    example.vizual_window()
    root.mainloop()