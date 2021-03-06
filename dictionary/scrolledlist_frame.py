import tkinter as tk
from tkinter import ttk
from autoscrollbar import AutoScrollbar


class ScrolledList(tk.Frame):
    """A scrolled list for displaying words."""

    def __init__(self, parent, handlerfcn, height):
        """Create an empty scrolled list.

        Arguments:
            parent: a parent tkinter widget
            handlerfcn: a function that does the search, takes a (str) argument
            height (int): height of the scrolled list in lines
        """
        super().__init__(parent)
        self.handlerfcn = handlerfcn
        self.height = height
        self.makeWidgets()

    def makeWidgets(self):
        """Create a treeview with a scrollbar."""
        sbar = AutoScrollbar(self, orient=tk.VERTICAL)
        treeview = ttk.Treeview(self,
                                height=self.height,
                                selectmode='browse',
                                show='tree')
        sbar.config(command=treeview.yview)
        treeview.config(yscrollcommand=sbar.set)

        sbar.grid(column=1, row=0)
        treeview.grid(column=0, row=0, sticky=tk.N+tk.E+tk.S+tk.W)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        treeview.bind('<Double-1>', self.handler)
        treeview.bind('<Return>', self.handler)
        self.treeview = treeview

    def handler(self, event):
        """Fetch the selection text and do the search."""
        iid = self.treeview.selection()[0]
        selection = self.treeview.item(iid, option='text')
        self.handlerfcn(selection)

    def setOptions(self, options):
        """Update the content of the scrolled list.

        Arguments:
            options: a list of strings
        """
        items = self.treeview.get_children()
        self.treeview.delete(*items)
        for option in options:
            self.treeview.insert("", tk.END, text=option)
