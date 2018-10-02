from tkinter import *
from tkinter import ttk
from autoscrollbar import AutoScrollbar


class ScrolledFrame(Frame):
    """A frame inside which is a canvas with scrollbars, inside which is an
    inner frame.
    """

    def __init__(self, parent, width, height, orient, border=False, **options):
        super().__init__(parent, **options)
        if border: self.configure(borderwidth=2, relief='groove')
        self.bgcolor = options.get('bg', self['bg'])
        
        # make a canvas with vertical and horizontal scrollbars
        vsbar = AutoScrollbar(self, orient=VERTICAL)
        hsbar = ttk.Scrollbar(self, orient=HORIZONTAL) # AutoScrollbar doesn't
                                                   # work here - wouldn't appear
        canvas = Canvas(self, width=width, height=height, # visible area size 
                              bg=self.bgcolor)
        vsbar.config(command=canvas.yview)
        hsbar.config(command=canvas.xview)
        self.hsbar = hsbar
        
        if orient == 'horizontal':
            self.rowconfigure(0, minsize=height)
            self.rowconfigure(1, minsize=40)
            canvas.config(xscrollcommand=hsbar.set)
            canvas.grid(column=0, row=0, sticky=N+E+S+W, columnspan=3)
        else:   # vertical:
            canvas.config(yscrollcommand=vsbar.set)
            canvas.grid(column=0, row=0, sticky=N+E+S+W)

        self.rowconfigure(0, weight=1)
        canvas.config(highlightthickness=0)
        self.canvas = canvas
        
        # enable scrolling the canvas with the mouse wheel
        self.canvas.bind_all('<Button-5>', self.onMouseWheelDown)
        self.canvas.bind_all('<Button-4>', self.onMouseWheelUp)
        
        # make the inner frame
        interior = Frame(canvas, 
                         bg = self.bgcolor, 
                         cursor='hand2')
        self.interior = interior
        interior_id = canvas.create_window((0, 0), window=interior, anchor=NW)
        
        def configureInterior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            # set the total canvas size
            canvas.config(scrollregion=(0, 0, size[0], size[1]))

            if orient == 'horizontal':
                # hide scrollbar when not needed
                if interior.winfo_reqwidth() <= canvas.winfo_width():
                    self.hsbar.grid_forget()
                else:
                    self.hsbar.grid(column=0, row=1, sticky=N+E+W, columnspan=3)
                    
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
        
        
