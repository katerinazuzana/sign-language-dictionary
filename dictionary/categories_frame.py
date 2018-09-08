from tkinter import *
from tkinter import ttk
import sqlite3
import os
import re
from scrolledlist_frame import ScrolledList


class CatFrm(Frame):
    """A frame where a word for translation might be selected from 
    a category or a subcategory of words.
    
    Contains:
    a category-combobox for choosing a category,
    a subcategory-combobox for choosing a corresponding subcategory,
    a scrolledlist displaying the words from the choosen (sub)category.
        
    The user selects the word to be translated from the scrolled list.
    On creation, a CatFrm instance takes a search function as an argument
    so that it can be called when a word is selected.
    """
    
    def __init__(self, dbpath, searchfcn, parent, **options):
        """Create a category selection combobox 'self.catcb',
                  a subcategory selection combobox 'self.subcacb' and
                  a 'self.scrolledlist'.
        
        Arguments: 
        dbpath -- [str] the database file path
        searchfcn -- a function that does the search,
                     takes one [str] argument
        parent -- the parent tkinter widget
        """
        super().__init__(parent, **options)
        self.dbpath = dbpath
        self.searchfcn = searchfcn
        self.width = 33
        self.height = 15   # scrolled list height in lines
        self.verticalSpace = 40  # space between widgets
        self.topSpace = 33       # additional padding at the top of the frame
        self.makeWidgets()
       
    def makeWidgets(self):    
        self.columnconfigure(0, weight=1)
        
        # create category combobox
        self.catvar = StringVar()
        self.catvar.set(' -- Zvolte kategorii --')
        self.catcb = ttk.Combobox(self, textvariable=self.catvar, 
                                        width=self.width,
                                        state='readonly')
        
        # set up the options available in category combobox
        self.catcb['values'] = self.findCats()
        
        self.catcb.bind('<<ComboboxSelected>>', self.catHandler)
        self.catcb.grid(column=0, row=0, 
                        sticky=N+E+S+W,
                        pady=(self.topSpace, self.verticalSpace))

        # create subcategory combobox, initially disabled
        self.subcatvar = StringVar()
        self.subcatvar.set(' -- Zvolte podkategorii --')
        self.subcatcb = ttk.Combobox(self,
                             textvariable=self.subcatvar,
                             state='disabled',
                             width=self.width)
        
        self.subcatcb.bind('<<ComboboxSelected>>', self.subcatHandler)
        self.subcatcb.grid(column=0, row=1, 
                           sticky=N+E+S+W, 
                           pady=(0, self.verticalSpace))
        
        # create empty scrolledlist
        self.scrolledlist = ScrolledList(self, 
                                         self.height, 
                                         self.searchfcn)
        self.scrolledlist.grid(column=0, row=2, sticky=N+E+S+W, 
                               pady=(0, self.verticalSpace))
        self.rowconfigure(2, weight=1)

    def findCats(self):
        """Look up available categories in the database and return
        a list of options for the category combobox."""
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT upperlevel FROM cathierarchy')
            find = cursor.fetchall()
        find = self.listOfTuplesToList(find)
        return self.leftPadItems(find)
    
    def catHandler(self, event):
        """Update the subcategory combobox and the scrolled list. 
        
        Set up the options available in the subcategory combobox.
        Reset the subcategory combobox variable to its default value.
        Update the options in the scrolledlist to all words
        of the selectected category.
        """
        subcats = self.findSubcats()       
        self.subcatcb['values'] = subcats
        self.subcatcb.config(state='readonly')
        self.subcatvar.set(' -- Zvolte podkategorii --')
        wordlist = self.findWords(self.catvar)
        self.scrolledlist.setOptions(wordlist)
    
    def findSubcats(self):
        """Find subcategories corresponding to the selected category."""
        cat = self.catvar.get().lstrip()
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT lowerlevel FROM cathierarchy WHERE \
                            upperlevel=?', (cat,))
            find = cursor.fetchall()
        find = self.listOfTuplesToList(find)
        return self.leftPadItems(find)

    def findWords(self, var):
        """Return a list of the words contained in a given (sub)category."""
        vartext = var.get().lstrip()
        if var == self.catvar:
            # looking up the words from a category
            SQLquery = 'SELECT word FROM words WHERE category IN \
                       (SELECT lowerlevel FROM cathierarchy WHERE upperlevel=?)'
        else:
            # looking up the words from a subcategory
            SQLquery = 'SELECT word FROM words WHERE category=?'
        
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute(SQLquery, (vartext,))
            find = cursor.fetchall()
        find = self.listOfTuplesToList(find)
        return self.mySort(find)

    def subcatHandler(self, event):
        """Update the options in the scrolledlist to the words
        of the selectected subcategory."""
        wordlist = self.findWords(self.subcatvar)
        self.scrolledlist.setOptions(wordlist)
        
    def mySort(self, alist):
        return sorted(alist, key = lambda x: (x[0].isdigit(), x.lower()))
    
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

        
        

