from tkinter import *
from autoscrollbar import AutoScrollbar


class ScrolledFrame(Frame):
    def __init__(self, parent, width, height, **options):
        super().__init__(parent)
        self.configure(borderwidth=2, relief='groove')
        
        # make a canvas with vertical and horizontal scrollbars
        vsbar = AutoScrollbar(self, orient=VERTICAL)
        hsbar = AutoScrollbar(self, orient=HORIZONTAL)
        canvas = Canvas(self, width=width, height=height, 
                              yscrollcommand=vsbar.set,
                              xscrollcommand=hsbar.set)
        vsbar.config(command=canvas.yview)
        hsbar.config(command=canvas.xview)
        
        vsbar.grid(column=1, row=0, sticky=N+S)
        hsbar.grid(column=0, row=1, sticky=E+W)
        canvas.grid(column=0, row=0, sticky=N+E+S+W)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
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
        """Roll the canvas down if the mouse pointer is over it."""
        if self.isMouseOverCanvas():
            self.canvas.yview_scroll(1, 'units')
        
    def onMouseWheelUp(self, event):
        """Roll the canvas up if the mouse pointer is over it."""
        if self.isMouseOverCanvas():
            self.canvas.yview_scroll(-1, 'units')
    
    def isMouseOverCanvas(self):
        x0, x1, y0, y1 = self.getCanvasCoords()
        x, y = self.winfo_pointerxy()
        return x0 < x < x1 and y0 < y < y1
    
    def getCanvasCoords(self):
#        self.canvas.update_idletasks() # update to get correct coords
        x0 = self.canvas.winfo_rootx()
        x1 = x0 + self.canvas.winfo_width() 
        y0 = self.canvas.winfo_rooty()
        y1 = y0 + self.canvas.winfo_height()
        return x0, x1, y0, y1
        
        
