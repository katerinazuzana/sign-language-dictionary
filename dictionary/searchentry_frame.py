from tkinter import *
import os
import sqlite3
from PIL import Image, ImageTk
from autocomplete_entry import AutocompleteEntry


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
        
        with Image.open(self.iconPath) as img:
            img = img.resize((self.iconSize, self.iconSize), 
                             Image.LANCZOS)
            self.iconImg = ImageTk.PhotoImage(img)
        
        Button(bfrm, image=self.iconImg,
                     command=self.startSearch
              ).grid(column=0, row=0, sticky=N+E+S+W)
        
        # create a list of all the words contained in the database
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT word FROM words')
            allwords = cursor.fetchall()
        entries = self.listOfTuplesToList(allwords)
        entries = self.leftPadItems(entries)
        
        # create the autocomplete entry
        self.var = StringVar()
        self.var.set(self.defaultText)
        self.ent = AutocompleteEntry(self, 
                                     entries, 
                                     self.startSearch, 
                                     maxEntries=10, 
                                     textvariable=self.var)
        self.ent.grid(column=0, row=0, sticky=N+E+W)
        self.ent.config(style="Gray.TEntry")
        
        self.ent.bind('<Return>', self.onEntryReturn)
                
        # on mouse click, delete the default text in the entry
        self.ent.bind('<Button-1>', self.onEntryClick)
        # when the user starts typing in the entry, delete the default text
        self.ent.bind('<Key>', self.onTyping)
        # on focus out of the entry, insert the default text back
        self.ent.bind('<FocusOut>', self.onFocusOut)

    def onEntryReturn(self, event):
        """Start the search only if there is some text in the entry."""
        if self.var.get() not in ('', self.defaultText):
            self.startSearch()

    def startSearch(self, event=None):
        """Hide the listbox, set focus on the entry and do the search."""
        if self.var.get() in ('', self.defaultText):
            # the user didn't enter any text
            self.master.showEnterText()
        else:
            self.ent.hideListboxWin()
            self.ent.focus_set()
            self.ent.icursor(END)
            self.searchfcn(self.var.get())
        
    def onEntryClick(self, event):
        """Delete the default text in the entry, if present."""
        if self.var.get() == self.defaultText:
            self.var.set('')
            self.ent.config(style="Black.TEntry")
    
    def onTyping(self, event):
        """Delete the default text in the entry, if present."""
        if self.var.get() == self.defaultText:
            self.ent.var.set('')
            self.ent.config(style="Black.TEntry")
        else:
            self.ent.update(event)
    
    def onFocusOut(self, event):
        """Insert the default text back into the entry, if it's empty.
        Hide the listbox.
        """
        if self.var.get() == '':
            self.var.set(self.defaultText)
            self.ent.config(style="Gray.TEntry")
            self.ent.hideListboxWin()
    
    def listOfTuplesToList(self, listOfTuples):    
        """Convert a list of 1-tuples into a simple list."""
        res = []
        for item in listOfTuples:
            res.append(item[0])
        return res

    def leftPadItems(self, alist):
        """Add a space to the begining of each string in a given list."""
        return [self.leftPad(item) for item in alist]
    
    def leftPad(self, word):
        """Add a space to the begining of a given string.""" 
        return " " + word




