from tkinter import *

class PlacementFrm(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.canvas = Canvas(self, width=240, 
                                   height=250, 
                                   borderwidth=2, 
                                   relief='groove')
        self.canvas.grid()
