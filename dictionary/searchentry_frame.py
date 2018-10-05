from tkinter import *
import os
import sqlite3
from autocomplete_entry import AutocompleteEntry
import tools


class EntFrm(Frame):
    """A frame with an entry and a search button.
    
    Used for entering the word to be searched in the Dictionary.
    On creation, takes a search function as an argument so that it
    can be called on Return/Search button press.
    """
    
    def __init__(self, dbpath, searchfcn, parent, imgdir, **options):
        """Create the AutocompleteEntry and the Search button.
        
        Arguments:
        dbpath -- [str] the database file path
        searchfcn -- a function that does the search,
                     takes one [str] argument
        parent -- the parent tkinter widget
        """
        super().__init__(parent, **options)
        self.dbpath = dbpath
        self.searchfcn = searchfcn
        self.defaultText = 'Zadejte výraz'
        self.iconPath = os.path.join(imgdir, 'search_icon.png')
        self.iconSize = 30
        self.makeWidgets()

    def makeWidgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # create the search button
        bfrm = Frame(self, height=30, width=60)
        bfrm.grid_propagate(0)  # size of child doesn't affect size of parent
        bfrm.grid(column=1, row=0, sticky=N)
        bfrm.rowconfigure(0, weight=1)
        
        self.iconImg = tools.getImage(self.iconPath, 
                                       width=self.iconSize, 
                                       height=self.iconSize)
        Button(bfrm, 
               image=self.iconImg,
               command=self.startSearch
               ).grid(column=0, row=0, sticky=N+E+S+W)
        
        # create a list of all the words contained in the database
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT word FROM words')
            allwords = cursor.fetchall()
        entries = tools.listOfTuplesToList(allwords)
        entries = tools.leftPadItems(entries)
        
        # create the autocomplete entry
        self.var = StringVar()
        self.var.set(self.defaultText)
        self.ent = AutocompleteEntry(self, 
                                     entries, 
                                     self.defaultText, 
                                     self.startSearch, 
                                     maxEntries=10, 
                                     textvariable=self.var)
        self.ent.grid(column=0, row=0, sticky=N+E+W)
        self.ent.config(style="Gray.TEntry")

    def startSearch(self, event=None):
        """Hide the listbox, set focus on the entry and do the search."""
        if self.var.get() in ('', self.defaultText):
            # the user didn't enter any text, prompt them to enter an expression
            self.master.showEnterText()
        else:
            self.ent.hideListboxWin()
            self.ent.focus_set()
            self.ent.icursor(END)
            self.searchfcn(self.var.get())


