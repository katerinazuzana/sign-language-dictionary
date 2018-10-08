from tkinter import *
from tkinter import ttk
import sqlite3
from scrolledlist_frame import ScrolledList
import tools


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
    
    def __init__(self, parent, dbpath, searchfcn, **options):
        """Create a category selection combobox 'self.catcb',
                  a subcategory selection combobox 'self.subcacb' and
                  a 'self.scrolledlist'.
        
        Arguments:
        parent -- the parent tkinter widget 
        dbpath -- [str] the database file path
        searchfcn -- a function that does the search,
                     takes one [str] argument
        """
        super().__init__(parent, **options)
        self.dbpath = dbpath
        self.searchfcn = searchfcn
        self.width = 33
        self.height = 14   # scrolled list height in lines
        self.verticalSpace = 40   # space between widgets
        self.topSpace = 10   # additional padding at the top of the frame
        self.makeWidgets()
       
    def makeWidgets(self):    
        self.columnconfigure(0, weight=1)  # empty column
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=2)  # empty column
        
        # empty rows:
        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(6, weight=3)
        
        # create category combobox
        self.catvar = StringVar()
        self.catvar.set(' -- Zvolte kategorii --')
        self.catcb = ttk.Combobox(self, 
                                  textvariable=self.catvar, 
                                  width=self.width,
                                  state='readonly')
        
        # set up the options available in category combobox
        self.catcb['values'] = self.findCats()
        
        self.catcb.bind('<<ComboboxSelected>>', self.catHandler)
        self.catcb.grid(column=1, row=1, 
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
        self.subcatcb.grid(column=1, row=3, 
                           sticky=N+E+S+W, 
                           pady=(0, self.verticalSpace))
        
        # create empty scrolledlist
        self.scrolledlist = ScrolledList(self, 
                                         self.searchfcn, 
                                         self.height)
        self.scrolledlist.grid(column=1, row=5, 
                               sticky=N+E+W, 
                               pady=(0, self.verticalSpace))
        self.rowconfigure(2, weight=1)
    
    def findCats(self):
        """Look up available categories in the database and return
        a list of options for the category combobox."""
        
        SQLquery = 'SELECT DISTINCT upperlevel FROM cathierarchy'
        return self.findCboxItems(SQLquery)
    
    def findSubcats(self):
        """Find subcategories corresponding to the selected category 
        and return a list of options for the subcategory combobox."""
        
        cat = self.catvar.get().lstrip()
        SQLquery = 'SELECT lowerlevel FROM cathierarchy WHERE \
                        upperlevel="{}"'.format(cat)
        return self.findCboxItems(SQLquery)
    
    def findCboxItems(self, SQLquery):
        """Return a list of options for a combobox."""
        
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute(SQLquery)
            find = cursor.fetchall()
        find = tools.listOfTuplesToList(find)
        return tools.leftPadItems(find)
    
    def catHandler(self, event):
        """Update the subcategory combobox and the scrolled list. 
        
        Set up the options available in the subcategory combobox.
        Reset the subcategory combobox variable to its default value.
        Update the options in the scrolledlist to all words
        of the selectected category.
        """
        self.catcb.selection_clear() # remove highlighting from the combobox
        subcats = self.findSubcats()       
        self.subcatcb['values'] = subcats
        self.subcatcb.config(state='readonly')
        self.subcatvar.set(' -- Zvolte podkategorii --')
        wordlist = self.findWords(self.catvar)
        self.scrolledlist.setOptions(wordlist)

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
        find = tools.listOfTuplesToList(find)
        return self.mySort(find)

    def subcatHandler(self, event):
        """Update the options in the scrolledlist to the words
        of the selectected subcategory."""
        self.subcatcb.selection_clear() # remove highlighting from the combobox
        wordlist = self.findWords(self.subcatvar)
        self.scrolledlist.setOptions(wordlist)
        
    def mySort(self, alist):
        return sorted(alist, key = lambda x: (x[0].isdigit(), x.lower()))
                

