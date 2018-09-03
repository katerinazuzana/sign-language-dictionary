from tkinter import *
from tkinter import ttk
import sqlite3
import os
import re
from scrolledlist_frame import ScrolledList


class CatFrm(Frame):
    """A frame containing:
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
        self.width = 35    # scrolled list width in characters
        self.height = 12   # scrolled list height in lines
        self.makeWidgets()
       
    def makeWidgets(self):    
        # create category combobox
        self.catvar = StringVar()
        self.catvar.set('-- Zvolte kategorii --')
        self.catcb = ttk.Combobox(self, textvariable=self.catvar, 
                                        width=self.width,
                                        state='readonly')
        
        # set up the options available in category combobox
        self.catcb['values'] = self.findCats()
        
        self.catcb.bind('<<ComboboxSelected>>', 
                        (lambda event: self.catHandler(self.catvar)))
        self.catcb.pack(side=TOP, fill=X, expand=YES, pady=(0, 40))

        # create subcategory combobox, initially disabled
        self.subcatvar = StringVar()
        self.subcatvar.set('-- Zvolte podkategorii --')
        self.subcatcb = ttk.Combobox(self,
                             textvariable=self.subcatvar,
                             state='disabled',
                             width=self.width)
        
        self.subcatcb.bind('<<ComboboxSelected>>',
                           (lambda event: self.subcatHandler(self.subcatvar)))
        self.subcatcb.pack(side=TOP, fill=X, expand=YES, pady=(0, 40))
        
        # create empty scrolledlist
        self.scrolledlist = ScrolledList([], self.searchfcn, 
                                             self.width, 
                                             self.height, 
                                             self)
        self.scrolledlist.pack(side=TOP, fill=BOTH, expand=YES)

    def findCats(self):
        """Look up available categories in the database and return
        a list of options for the category combobox."""
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT upperlevel FROM cathierarchy')
            find = cursor.fetchall()
        return self.listOfTuplesToList(find)
    
    def catHandler(self, catvar):
        """Update the subcategory combobox and the scrolled list. 
        
        Receive the category combobox variable and according to its value,
        set up the options available in the subcategory combobox.
        Reset the subcategory combobox variable to its default value.
        Update the options in the scrolledlist to all words
        of the selectected category.
        """
        subcats = self.findSubcats(catvar.get())       
        self.subcatcb['values'] = subcats
        self.subcatcb.config(state='readonly')
        self.subcatvar.set('-- Zvolte podkategorii --')
        wordlist = self.findWordsInCat(catvar.get())
        wordlist = self.mySort(wordlist)      
        self.scrolledlist.setOptions(wordlist)
    
    def findSubcats(self, cat):
        """Receive a string with the selected category and return a list
        of corresponding subcategories looked up in the database."""
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT lowerlevel FROM cathierarchy WHERE \
                            upperlevel=?', (cat,))
            find = cursor.fetchall()
        return self.listOfTuplesToList(find)

    def findWordsInCat(self, cat):
        """Receive a string with the selected category and return a list
        of this category's words looked up in the database."""
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT word FROM words WHERE category IN \
                            (SELECT lowerlevel FROM cathierarchy WHERE \
                            upperlevel=?)', (cat,))
            find = cursor.fetchall()
        return self.listOfTuplesToList(find)

    def subcatHandler(self, subcatvar):
        """Update the options in the scrolledlist to the words
        of the selectected subcategory."""
        wordlist = self.findWordsInSubcat(subcatvar.get())
        wordlist = self.mySort(wordlist)
        self.scrolledlist.setOptions(wordlist)
        
    def findWordsInSubcat(self, subcat):
        """Receive a string with the selected subcategory and return a list
        of this subcategory's words looked up in the database."""
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT word FROM words WHERE category=?',(subcat,))
            find = cursor.fetchall()
        return self.listOfTuplesToList(find)
        
    def mySort(self, alist):
        return sorted(alist, key = lambda x: (x[0].isdigit(), x.lower()))
    
    def listOfTuplesToList(self, listOfTuples):    
        """Convert a list of 1-tuples into a simple list."""
        res = []
        for item in listOfTuples:
            res.append(item[0])
        return res
        
        

        
        

