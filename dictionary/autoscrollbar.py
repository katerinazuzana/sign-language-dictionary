from tkinter import *
from tkinter.ttk import *


class AutoScrollbar(Scrollbar):
    """A scrollbar that hides itself if it's not needed."""
    
    def set(self, low, high):
        if float(low) <= 0 and float(high) >= 1:
            self.grid_forget()
        else:
            if self.cget('orient') == HORIZONTAL:
                self.grid(column=0, row=1, sticky=E+W)
            else:
                self.grid(column=1, row=0, sticky=N+S)
        Scrollbar.set(self, low, high)

