from tkinter import *
import os
import sqlite3
from autocomplete_entry import AutocompleteEntry


class EntFrm(Frame):
    """A frame with an entry and a search button.
    
    Used for entering the word to be searched in the Dictionary.
    On creation, takes a search function as an argument so that it
    can be called on Return/Search button press.
    """
    
    def __init__(self, dbpath, searchfcn, parent, **options):
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
        self.makeWidgets()

    def makeWidgets(self):
        self.columnconfigure(0, weight=1)        
        self.rowconfigure(0, minsize=140)
        
        # create the search button
        bfrm = Frame(self, height=30, width=90)
        bfrm.grid_propagate(0)  # don't shrink
        bfrm.grid(column=1, row=0, sticky=N)
        bfrm.rowconfigure(0, weight=1)
        
        Button(bfrm, text='Vyhledat',
                     command=(lambda: self.startSearch(self.var.get()))
              ).grid(column=0, row=0, sticky=N+E+S+W)
        
        # create a list of all the words contained in the database
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT word FROM words')
            allwords = cursor.fetchall()
        entries = self.listOfTuplesToList(allwords)
        
        # create the autocomplete entry
        self.ent = AutocompleteEntry(self)
        self.ent.build(entries, max_entries=4, no_results_message=None)
        self.ent.grid(column=0, row=0, sticky=N+E+W)
        
        # set the entry variable
        self.var = self.ent.text
        self.var.set(self.defaultText)
        self.ent.entry.config(fg='grey')
        
        self.ent.entry.bind('<Return>',
                      (lambda event: self.startSearch(self.var.get())))
        self.ent.listbox.bind('<Return>',
                      (lambda event: self.startSearch(self.var.get())))
        self.ent.listbox.bind('<Double-Button>',
                      (lambda event: self.startSearch(self.var.get())))
                
        # on mouse click, delete the default text in the entry
        self.ent.entry.bind('<Button-1>', (lambda event: self.onEntryClick()))
        # when the user starts typing in the entry, delete the default text
        self.ent.entry.bind('<Key>', (lambda event: self.onTyping(event)))
        # on focus out of the entry, insert the default text back
        self.ent.entry.bind('<FocusOut>', (lambda event: self.onFocusOut()))

    def startSearch(self, var):
        """Hide the listbox, set focus on the entry and do the search."""
        self.ent.listbox.grid_forget()
        self.ent.entry.focus_set()
        self.ent.entry.icursor(END)
        self.searchfcn(self.var.get())
        
    def onEntryClick(self):
        """Delete the default text in the entry, if present."""
        if self.var.get() == self.defaultText:
            self.var.set('')
            self.ent.entry.config(fg='black')
    
    def onTyping(self, event):
        """Delete the default text in the entry, if present."""
        if self.var.get() == self.defaultText:
            self.var.set('')
            self.ent.entry.config(fg='black')
        else:
            self.ent.update_autocomplete(event)
    
    def onFocusOut(self):
        """Insert the default text back into the entry, if it's empty.
        Hide the listbox.
        """
        if self.var.get() == '':
            self.var.set(self.defaultText)
            self.ent.entry.config(fg='grey')
            self.ent.listbox.grid_forget()
    
    def listOfTuplesToList(self, listOfTuples):    
        """Convert a list of 1-tuples into a simple list."""
        res = []
        for item in listOfTuples:
            res.append(item[0])
        return res





