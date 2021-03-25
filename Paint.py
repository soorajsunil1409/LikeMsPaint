from tkinter import *
from tkinter import colorchooser, filedialog
from PIL import ImageGrab, ImageTk, Image, ImageDraw
from time import sleep
from math import sqrt

class MainWindow(Tk):
    old_x = None
    old_y = None
    color = "black"
    first_x, first_y, last_x, last_y = None, None, None, None
    f_x, f_y, l_x, l_y = None, None, None, None
    nw, ne, se, sw = None, None, None, None
    point_x, point_y = None, None
    objects = []
    selected = False
    selected_obj = None
    fill = None
    handle_const = 15
    doted = False
    event = None

    def __init__(self):
        super().__init__()

        self.geometry("600x650")
        self.title("Painter")

        self.line_widths = range(2, 21, 2)
        self.eraser_widths = range(10, 40, 10)
        self.drawings_ = ["None", "Rect", "Circle", "Line", "Dotted Line"]
        self.def_eraser_width = IntVar()
        self.def_eraser_width.set(self.eraser_widths[0])
        self.def_line_width = IntVar()
        self.def_line_width.set(self.line_widths[0])
        self.def_drawings = StringVar()
        self.def_drawings.set(self.drawings_[0])
        self.eraser_var = IntVar()

        self.setup_ui()

        self.mainloop()

    def setup_ui(self):
        self.toolbar = Frame()
        self.toolbar.config(bg="red")
        self.toolbar.place(x=0, y=0, relwidth=1.0, height=100)
        self.setup_toolbar_items()

        self.canvas = Canvas(self, bg="white")
        self.canvas.place(x=0, y=100, relwidth=1.0, relheight=0.896)

        self.menu = Menu(self)

        self.config(menu=self.menu)

        self.canvas.bind("<ButtonRelease-1>", self.release)
        self.canvas.bind("<Button-1>", self.draw_down)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<Double-Button-1>", self.delete_obj)
        #self.bind("<Command-s>", self.getter)

    def setup_toolbar_items(self):
        self.lbl_width = Label(self.toolbar, text="Line Width: ")
        self.lbl_width.place(rely=0.25-(12.5/100), x=10, height=25, width=85)
        self.line_width_selector = OptionMenu(self.toolbar, self.def_line_width, *self.line_widths)
        self.line_width_selector.place(rely=0.25-(12.5/100), x=95, height=25, width=45)

        self.color_lbl = Label(self.toolbar, bg="black")
        self.color_lbl.place(rely=0.25-(12.5/100), x=243, height=25, width=25)
        self.color_selector_btn = Button(self.toolbar, text="Select Color: ", command=lambda: self.select_color(self.color_lbl, "color"))
        self.color_selector_btn.place(rely=0.25-(12.5/100), x=157, height=25, width=85)

        self.eraser_lbl = Label(self.toolbar, text="Eraser:")
        self.eraser_lbl.place(rely=0.25-(12.5/100), x=285, height=25, width=55)
        self.eraser_check = Checkbutton(self.toolbar, onvalue=1, offvalue=0, var=self.eraser_var)
        self.eraser_check.place(rely=0.25-(12.5/100), x=340, height=25, width=20)
        self.eraser_width_selector = OptionMenu(self.toolbar, self.def_eraser_width, *self.eraser_widths)
        self.eraser_width_selector.place(rely=0.25-(12.5/100), x=360, height=25)

        self.drawings = OptionMenu(self.toolbar, self.def_drawings, *self.drawings_)
        self.drawings.place(rely=0.25-(12.5/100), x=430, width=65)

        self.fill_color_lbl = Label(self.toolbar, bg="black")
        self.fill_color_lbl.place(rely=0.55-(12.5/100), x=470, height=25, width=25)
        self.fill_color_btn = Button(self.toolbar, text="Fill: ", command=lambda: self.select_color(self.fill_color_lbl, "fill"))
        self.fill_color_btn.place(rely=0.55-(12.5/100), x=430, height=25, width=38)

        self.clear_fill_btn = Button(self.toolbar, text="Clear Fill: ", command=self.clear_fill)
        self.clear_fill_btn.place(rely=0.85-(12.5/100), x=430, height=25, width=65)

        self.clear_btn = Button(self.toolbar, text="Clear All", command=self.clear_all)
        self.clear_btn.place(rely=0.25-(12.5/100), x=505, height=25, width=85)

    def clear_fill(self):
        self.fill = None
        self.fill_color_lbl.config(bg="Black")

    def select_color(self, lbl, type_):
        clr = colorchooser.askcolor()
        clr = clr[1]

        if type_ == "color":
            self.color = clr
        elif type_ == "fill":
            self.fill = clr

        lbl.config(bg=clr)

    def clear_all(self):
        self.canvas.delete("all")
        self.objects.clear()
        self.first_x, self.first_y, self.last_x, self.last_y = None, None, None, None
        self.nw, self.ne, self.se, self.sw = None, None, None, None
        self.selected = False
        self.point_x, self.point_y = None, None
        self.selected_obj = None
        self.doted = False

    def drag(self, event):
        if self.selected:
            for rects in self.objects:
                if rects[1] == self.selected_obj:
                    sel_rect = rects

            print(sel_rect, "yes")
            
            self.resize(10, sel_rect, event, sel_rect[0])
            return
        
        self.paint(event)
        self.selected_obj = None
        self.selected = False
        
    def resize(self, len_, sel_rect, event, shape):
        right_mid_y = (sel_rect[9] + sel_rect[5]) / 2
        top_mid_x = (sel_rect[2] + sel_rect[8]) / 2

        if shape == "oval":
            self.side_resize(sel_rect, right_mid_y, event, top_mid_x)
        else:
            self.corner_resize(sel_rect, len_, event, top_mid_x, right_mid_y)

        print(self.objects)

    def corner_resize(self, sel_rect, len, event, top_mid_x, right_mid_y):
        if abs(self.point_x - sel_rect[2]) < len and abs(self.point_y - sel_rect[3]) < len:
            print("Yes")
            self.objects.pop(self.objects.index(sel_rect))
            self.canvas.coords(self.selected_obj, sel_rect[4], sel_rect[5], event.x, event.y)
            self.objects.append([sel_rect[0], sel_rect[1], event.x, event.y, sel_rect[4], sel_rect[5], sel_rect[6], sel_rect[7], sel_rect[4], event.y, event.x, sel_rect[5]])
            self.point_x, self.point_y = event.x, event.y

        elif abs(self.point_x - sel_rect[4]) < len and abs(self.point_y - sel_rect[5]) < len:
            self.objects.pop(self.objects.index(sel_rect))
            self.canvas.coords(self.selected_obj, event.x, event.y, sel_rect[2], sel_rect[3])
            self.objects.append([sel_rect[0], sel_rect[1], sel_rect[2], sel_rect[3], event.x, event.y, sel_rect[6], sel_rect[7], event.x, sel_rect[3], sel_rect[2], event.y])
            self.point_x, self.point_y = event.x, event.y

        elif abs(self.point_x - sel_rect[4]) < 10 and abs(self.point_y - sel_rect[3]) < 10:
            self.objects.pop(self.objects.index(sel_rect))
            self.canvas.coords(self.selected_obj, sel_rect[10], sel_rect[11], event.x, event.y)
            self.objects.append([sel_rect[0], sel_rect[1], sel_rect[10], event.y, event.x, sel_rect[11], sel_rect[6], sel_rect[7], event.x, event.y, sel_rect[10], sel_rect[11]])
            self.point_x, self.point_y = event.x, event.y

        elif abs(self.point_x - sel_rect[2]) < 10 and abs(self.point_y - sel_rect[5]) < 10:
            self.objects.pop(self.objects.index(sel_rect))
            self.canvas.coords(self.selected_obj, event.x, event.y, sel_rect[4], sel_rect[3])
            self.objects.append([sel_rect[0], sel_rect[1], event.x, sel_rect[3], sel_rect[4], event.y, sel_rect[6], sel_rect[7], sel_rect[4], sel_rect[3], event.x, event.y])
            self.point_x, self.point_y = event.x, event.y

        else:
            self.side_resize(sel_rect, right_mid_y, event, top_mid_x)

    def side_resize(self, sel_rect, right_mid_y, event, top_mid_x):
        if abs(self.point_x - sel_rect[4]) < self.handle_const and abs(self.point_y - right_mid_y) < self.handle_const:
            self.objects.pop(self.objects.index(sel_rect))
            self.canvas.coords(self.selected_obj, event.x, sel_rect[5], sel_rect[2], sel_rect[3])
            self.objects.append([sel_rect[0], sel_rect[1], sel_rect[2], sel_rect[3], event.x, sel_rect[5], sel_rect[6], sel_rect[7], event.x, sel_rect[9], sel_rect[10], sel_rect[11]])
            self.point_x, self.point_y = event.x, right_mid_y

        elif abs(self.point_x - sel_rect[2]) < self.handle_const and abs(self.point_y - right_mid_y) < self.handle_const:
            self.objects.pop(self.objects.index(sel_rect))
            self.canvas.coords(self.selected_obj, sel_rect[8], sel_rect[5], event.x, sel_rect[3])
            self.objects.append([sel_rect[0], sel_rect[1], event.x, sel_rect[3], sel_rect[4], sel_rect[5], sel_rect[6], sel_rect[7], sel_rect[8], sel_rect[9], event.x, sel_rect[11]])
            self.point_x, self.point_y = event.x, right_mid_y

        elif abs(self.point_x - top_mid_x) < self.handle_const and abs(self.point_y - sel_rect[3]) < self.handle_const:
            self.objects.pop(self.objects.index(sel_rect))
            self.canvas.coords(self.selected_obj, sel_rect[4], sel_rect[5], sel_rect[2], event.y)
            self.objects.append([sel_rect[0], sel_rect[1], sel_rect[2], event.y, sel_rect[4], sel_rect[5], sel_rect[6], sel_rect[7], sel_rect[8], event.y, sel_rect[10], sel_rect[11]])
            self.point_x, self.point_y = top_mid_x, event.y

        elif abs(self.point_x - top_mid_x) < self.handle_const and abs(self.point_y - sel_rect[11]) < self.handle_const:
            self.objects.pop(self.objects.index(sel_rect))
            self.canvas.coords(self.selected_obj, sel_rect[4], event.y, sel_rect[2], sel_rect[3])
            self.objects.append([sel_rect[0], sel_rect[1], sel_rect[2], sel_rect[3], sel_rect[4], event.y, sel_rect[6], sel_rect[7], sel_rect[8], sel_rect[9], sel_rect[10], event.y])
            self.point_x, self.point_y = top_mid_x, event.y

    def select(self, obj):
        if not self.selected:
            self.selected = True
            self.selected_obj = obj
    
    def delete_obj(self, e):
        if self.selected_obj:
            self.canvas.delete(self.selected_obj)
            for obj in self.objects:
                if obj[1] == self.selected_obj:
                    self.objects.pop(self.objects.index(obj))
            self.selected_obj = None
            self.selected = False

    def draw_down(self, event):
        if self.eraser_var.get() == 0 and not self.selected:
            if self.def_drawings.get() == "Rect":
                self.first_x = event.x
                self.first_y = event.y
            elif self.def_drawings.get() == "Circle":
                self.first_x = event.x
                self.first_y = event.y
            elif self.def_drawings.get() == "Line" or self.def_drawings.get() == "Dotted Line":
                self.first_x = event.x
                self.first_y = event.y

        self.point_x, self.point_y = event.x, event.y
        print(self.point_x, self.point_y)

    def draw_up(self, event):
        try:
            if not self.selected and self.eraser_var.get() == 0:
                if self.def_drawings.get() == "Rect":
                    self.draw_rect(event)

                elif self.def_drawings.get() == "Circle":
                    self.draw_oval(event)

                elif self.def_drawings.get() == "Line" or self.def_drawings.get() == "Dotted Line":
                    self.draw_line(event)
        except:
            pass
        

        self.first_x, self.first_y, self.last_x, self.last_y = None, None, None, None
        self.f_x, self.f_y, self.l_x, self.l_y = None, None, None, None

    def draw_line(self, event):
        self.last_x = event.x
        self.last_y = event.y
        
        if self.doted:
            line = self.canvas.create_line(self.first_x, self.first_y, self.last_x, self.last_y, fill=self.color, width=self.def_line_width.get(), dash=(5,10))
        else:
            line = self.canvas.create_line(self.first_x, self.first_y, self.last_x, self.last_y, fill=self.color, width=self.def_line_width.get())
        
        self.canvas.tag_bind(line, "<Button-1>", lambda arg: self.select(line))

        self.objects.append(["line", line, self.first_x, self.first_y, self.last_x, self.last_y, self.color, self.def_line_width.get(), self.last_x, self.first_y, self.first_x, self.last_y])
        self.canvas.tag_raise(line)

        self.canvas.delete("test")

    def draw_rect(self, event):
        self.last_x = event.x
        self.last_y = event.y
        
        rect = self.canvas.create_rectangle(self.first_x, self.first_y, self.last_x, self.last_y, outline=self.color, width=self.def_line_width.get(), fill=self.fill)
        
        self.canvas.tag_bind(rect, "<Button-1>", lambda arg: self.select(rect))
        self.canvas.tag_bind(rect, "<B1-Motion>", lambda arg: self.drag)
        self.canvas.tag_bind(rect, "<ButtonRelease-1>", lambda arg: self.release)

        self.objects.append(["rect", rect, self.first_x, self.first_y, self.last_x, self.last_y, self.color, self.def_line_width.get(), self.last_x, self.first_y, self.first_x, self.last_y])
        self.canvas.tag_raise(rect)

        print(self.objects)

        self.canvas.delete("test")

    def draw_oval(self, event):
        self.last_x = event.x
        self.last_y = event.y
        
        oval = self.canvas.create_oval(self.first_x, self.first_y, self.last_x, self.last_y, outline=self.color, width=self.def_line_width.get(), fill=self.fill)

        self.canvas.tag_bind(oval, "<Button-1>", lambda arg: self.select(oval))

        self.objects.append(["oval", oval, self.first_x, self.first_y, self.last_x, self.last_y, self.color, self.def_line_width.get(), self.last_x, self.first_y, self.first_x, self.last_y])
        self.canvas.tag_raise(oval)

        self.canvas.delete("test")

    def paint(self, event):
        try:
            line_width = self.def_line_width.get() if self.eraser_var.get() == 0 else self.def_eraser_width.get()
            line_color = self.color if self.eraser_var.get() == 0 else "white"

            if self.def_drawings.get() == "None" or self.eraser_var.get() == 1:
                if self.old_x and self.old_y:
                    self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                            width=line_width, fill=line_color,
                                            capstyle=ROUND, smooth=FALSE, splinesteps=36)

                self.old_x = event.x
                self.old_y = event.y

            elif self.eraser_var.get() == 0:
                if self.def_drawings.get() == "Rect":
                    self.create_rect_visual(event)

                elif self.def_drawings.get() == "Circle":
                    self.create_oval_visual(event)
                
                elif self.def_drawings.get() == "Line" or self.def_drawings.get() == "Dotted Line":
                    if self.def_drawings.get() == "Dotted Line":
                        self.doted = True
                    self.create_visual_line(event)
        except:
                pass

    def create_visual_line(self, event):
        if self.f_x != None and self.f_y != None and self.l_x != None and self.l_y != None:
            self.canvas.delete("test")

        if self.doted:
            self.canvas.create_line(self.first_x, self.first_y, event.x, event.y,
                                    width=self.def_line_width.get(), fill=self.color, tags=("test"), dash=(5,10))
        else:
            self.canvas.create_line(self.first_x, self.first_y, event.x, event.y,
                                    width=self.def_line_width.get(), fill=self.color, tags=("test"))

        self.f_x, self.f_y, self.l_x, self.l_y = self.first_x, self.first_y, event.x, event.y

    def create_oval_visual(self, event):
        if self.f_x != None and self.f_y != None and self.l_x != None and self.l_y != None:
            self.canvas.delete("test")

        self.canvas.create_oval(self.first_x, self.first_y, event.x, event.y,
                                    width=self.def_line_width.get(), outline=self.color, tags=("test"), fill=self.fill)

        self.f_x, self.f_y, self.l_x, self.l_y = self.first_x, self.first_y, event.x, event.y

    def create_rect_visual(self, event=None):
        if self.f_x != None and self.f_y != None and self.l_x != None and self.l_y != None:
            self.canvas.delete("test")

        self.canvas.create_rectangle(self.first_x, self.first_y, event.x, event.y,
                                    width=self.def_line_width.get(), outline=self.color, tags=("test"), fill=self.fill)

        self.f_x, self.f_y, self.l_x, self.l_y = self.first_x, self.first_y, event.x, event.y

    '''def getter(self, event):
        x=self.winfo_rootx()+self.canvas.winfo_x()
        y=self.winfo_rooty()+self.canvas.winfo_y()
        x1=x+self.canvas.winfo_width()
        y1=y+self.canvas.winfo_height()

        filename = filedialog.asksaveasfilename(initialdir="/Users/soorajsunil/Desktop", defaultextension=".png")
        
        if not filename:
            return
        ImageGrab.grab().crop((x,y,x1,y1)).save(filename)'''

    def release(self, event):
        if self.def_drawings.get() == "None":
            self.old_x, self.old_y = None, None
        else:
            self.draw_up(event)
        if self.selected:
            self.selected = False
            self.selected_obj = None
            self.point_x, self.point_y = None, None

if __name__ == "__main__":
    app = MainWindow()