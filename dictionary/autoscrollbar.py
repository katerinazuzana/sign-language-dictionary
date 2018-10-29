import tkinter as tk
from tkinter import ttk


class AutoScrollbar(ttk.Scrollbar):
    """A scrollbar that hides itself if it's not needed."""

    def set(self, low, high):
        if float(low) <= 0 and float(high) >= 1:
            self.grid_forget()
        else:
            if self.cget('orient') == tk.HORIZONTAL:
                self.grid(column=0, row=1, sticky=tk.E+tk.W)
            else:
                self.grid(column=1, row=0, sticky=tk.N+tk.S)
        ttk.Scrollbar.set(self, low, high)
