from tkinter import *
from tkinter import ttk
from autoscrollbar import AutoScrollbar


class ScrolledList(Frame):
    """A scrolled list displaying a list of words. When a word is 
    double-clicked, the searchfcn is called on the choosen word.
    """
    
    def __init__(self, parent, searchfcn, height):
        """Create an empty scrolled list.
        
        Arguments:
        parent -- the parent tkinter widget
        searchfcn -- a function that takes a string as an argument
        height -- [int] height of the scrolled list in lines
        """
        super().__init__(parent)
        self.searchfcn = searchfcn
        self.height = height
        self.makeWidgets()

    def makeWidgets(self):
        # create a scrollbar and a treeview
        sbar = AutoScrollbar(self, orient=VERTICAL)
        treeview = ttk.Treeview(self,                                 
                                height=self.height,  
                                selectmode='browse', 
                                show='tree')
        # cross link them
        sbar.config(command=treeview.yview)    
        treeview.config(yscrollcommand=sbar.set)
        
        sbar.grid(column=1, row=0)
        treeview.grid(column=0, row=0, sticky=N+E+S+W)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
            
        treeview.bind('<Double-1>', self.handler)
        treeview.bind('<Return>', self.handler)
        self.treeview = treeview

    def handler(self, event):
        """Fetch the selection text and call the search."""
        iid = self.treeview.selection()[0]
        selection = self.treeview.item(iid, option='text')
        self.searchfcn(selection)       

    def setOptions(self, options):
        """Update the options of the scrolled list.
        
        Arguments:
        options -- a list of strings
        """
        items = self.treeview.get_children()
        self.treeview.delete(*items)
        for option in options:
            self.treeview.insert("", END, text=option)

