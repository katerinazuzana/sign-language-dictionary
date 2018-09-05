from tkinter import *
from autoscrollbar import AutoScrollbar


class ScrolledList(Frame):
    """A scrolled list displaying a list of words passed in as 'options'
    argument. When a word is double-clicked, the searchfcn is called
    on the choosen word.
    """
    
    def __init__(self, options, searchfcn, width, height, parent):
        """Create a scrolled list.
        
        Arguments:
        options -- a list of strings
        searchfcn -- a function that takes a string as an argument
        width -- [int] width of the scrolled list in characters
        height -- [int] height of the scrolled list in lines
        parent -- the parent tkinter widget
        """
        super().__init__(parent)
        self.searchfcn = searchfcn
        self.width = width
        self.height = height
        self.makeWidgets(options)

    def makeWidgets(self, options):
        # create a scrollbar and a listbox
        sbar = AutoScrollbar(self, orient=VERTICAL)
        listbox = Listbox(self, width=self.width, height=self.height)
        # cross link them
        sbar.config(command=listbox.yview)    
        listbox.config(yscrollcommand=sbar.set)
        
        sbar.grid(column=1, row=0)
        listbox.grid(column=0, row=0, sticky=N+E+S+W)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        for option in options:
            listbox.insert(END, option)
            
        listbox.bind('<Double-1>', self.handler)
        listbox.bind('<Return>', self.handler)
        self.listbox = listbox

    def handler(self, event):
        index = self.listbox.curselection()
        selection = self.listbox.get(index)    # fetch the selection text
        self.searchfcn(selection.lstrip())     # and call the search

    def setOptions(self, options):
        """Update the options of the scrolled list.
        
        Arguments:
        options -- a list of strings
        """
        self.listbox.delete(0, END)
        for option in options:             
            self.listbox.insert(END, option)

