from tkinter import *
from autoscrollbar import AutoScrollbar


class ScrolledFrame(Frame):
    def __init__(self, parent, width, height, **options):
        super().__init__(parent)
        self.configure(borderwidth=2, relief='groove')
        
        # make a canvas and a scrollbar
        sbar = AutoScrollbar(self, orient=VERTICAL)
        canvas = Canvas(self, width=width, height=height, 
                              yscrollcommand=sbar.set)
        sbar.config(command=canvas.yview)
        
        sbar.grid(column=1, row=0, sticky=N+S)
        canvas.grid(column=0, row=0, sticky=N+E+S+W)
        self.columnconfigure(0, weight=1)
        
        canvas.config(highlightthickness=0)
        self.canvas = canvas
        
        # enable scrolling the canvas with the mouse wheel
        self.canvas.bind_all('<Button-5>', self.onMouseWheelDown)
        self.canvas.bind_all('<Button-4>', self.onMouseWheelUp)
        
        # make the inner frame
        interior = Frame(canvas, 
                         bg = 'white', 
                         cursor='hand2') # set a cursor
        self.interior = interior
        interior_id = canvas.create_window((0, 0), window=interior, anchor=NW)
        
        def configureInterior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion=(0, 0, size[0], size[1]))
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's height to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', configureInterior)

    def onMouseWheelDown(self, event):
        self.canvas.yview_scroll(1, 'units')
        x, y = self.winfo_pointerxy()

        
    def onMouseWheelUp(self, event):
        self.canvas.yview_scroll(-1, 'units')
        
        x0 = self.canvas.winfo_rootx()
        x1 = x0 + self.canvas.winfo_width() 
        y0 = self.canvas.winfo_rooty()
        y1 = y0 + self.canvas.winfo_height()
        
        x, y = self.winfo_pointerxy()
        print(x0 < x < x1, y0 < y < y1)
        
        
        
