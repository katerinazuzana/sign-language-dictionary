#######################################################################
#                                                      
# Czech Sign Language Dictionary 
#                                                      
#######################################################################


from tkinter import *
from tkinter import ttk
import sqlite3
import os
from search_engine import SearchEngine
from main_frame import MainFrm
from categories_frame import CatFrm
from sign_input_frame import SignInputFrm
import math


class Dictionary():
    """A Czech Sign Language Dictionary application.
            
    Constants:
    BORDER -- the main frame border
    WIN_MIN_WIDTH -- minimal width of the main application window
    WIN_MIN_HEIGHT -- minimal height of the main application window
    TAB_PAD -- initial notebook's tab padding
    BGCOLOR -- background color
    """

    BORDER = 40
    WIN_MIN_WIDTH = 985
    WIN_MIN_HEIGHT = 700
    TAB_PAD = 23
    BGCOLOR = 'white'

    def __init__(self, dbpath, vfdir, imgdir):
        """Build the application window.
        
        Arguments:
        dbpath -- [str] the database file path
        vfdir -- [str] path to the directory where video files 
                 with translations to sign language are located
        imgdir -- [str] path to the directory where images are located
        """
        self.dbpath = dbpath
        self.vfdir = vfdir
        self.imgdir = imgdir
        
        self.altsmax = 10  # maximum number of alternative options
        self.font = ('Helvetica', 12)
        
        # the SearchEngine object provides the logic behind the dictionary app
        self.searchEng = SearchEngine(self.dbpath, 
                                      self.vfdir, 
                                      self.altsmax)
        self.makeWidgets()
        
    def makeWidgets(self):
        # build the application window
        self.root = Tk()
        self.root.title('Slovník českého znakového jazyka')
        self.root.option_add('*Font', self.font)
        self.root.minsize(width = self.WIN_MIN_WIDTH, 
                          height = self.WIN_MIN_HEIGHT)
             
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # create the main frame
        self.mainfrm = MainFrm(self.root, 
                             self.dbpath, 
                             self.vfdir, 
                             self.imgdir, 
                             self.searchEng.search, 
                             self.altsmax, 
                             self.BORDER, 
                             bg=self.BGCOLOR, 
                             padx=self.BORDER)
        self.mainfrm.grid(column=0, row=0, sticky=N+E+S+W)
        
        # when the searchEng is done searching, it calls a function to show
        # the result - these functions are defined in the mainfrm object
        self.searchEng.showResultFcn = self.mainfrm.showResult
        self.searchEng.showSignsFcn = self.mainfrm.showSigns
        
        # create notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(column=1, row=0, sticky=N+E+S+W)
        
        # style
        self.style = style = ttk.Style()
        style.theme_use('clearlooks')
        
        style.configure('Gray.TEntry', foreground='gray')
        style.configure('Black.TEntry', foreground='black')
        
        style.configure('TCombobox', padding=(0, -4, 0, -4), 
                                     background=self.BGCOLOR)
        
        style.configure('Treeview', background=self.BGCOLOR, 
                                    padding=(0, 2, 0, 4))
        style.map('Treeview', background=[('selected', 'lightgrey')])
        style.configure('Treeview.Item', padding=(-15, -5, 0, 0))
        
        style.configure('TNotebook.Tab', padding=(self.TAB_PAD, 0, 
                                                  self.TAB_PAD, 0))
        style.map('TNotebook.Tab', padding=[('selected', (self.TAB_PAD, 0, 
                                             self.TAB_PAD, 0))])
            
        # tabs' font:
        style.configure('.', font=self.font)
        # color visible only at the notebook border:
        style.configure('TNotebook', background=self.BGCOLOR)
        # color of the non-selected tab:
        style.configure('TNotebook.Tab', background='ghost white')
        # active tab background:
        style.map('TNotebook.Tab', background=[('selected', self.BGCOLOR)])
        
        # create the category-selection frame
        self.catfrm = CatFrm(self.dbpath, 
                             self.searchEng.search, 
                             self.notebook, 
                             bg=self.BGCOLOR, 
                             padx=self.BORDER, 
                             pady=self.BORDER)
        self.catfrm.grid(column=0, row=0, sticky=N+E+S+W)
        self.notebook.add(self.catfrm, text='Výběr podle kategorií')
        
        # create the sign-input frame
        self.signfrm = SignInputFrm(self.notebook,  
                                    self.imgdir, 
                                    self.searchEng.signSearch, 
                                    bg=self.BGCOLOR, 
                                    padx=self.BORDER)
        self.signfrm.grid(column=0, row=0, sticky=N+E+S+W)
        self.notebook.add(self.signfrm, text='Překlad z ČZJ do ČJ')
        
        # bind tab padding recalculation to notebook resizing
        self.notebook.update_idletasks()
        self.notebook.initialWidth = self.notebook.winfo_width()
        self.notebook.bind('<Configure>', self.onResize)
        
    def onResize(self, event):
        """Dynamically set tab padding to streach tabs over whole notebook."""
        width = self.notebook.winfo_width()
        extraPadding = math.ceil((width - self.notebook.initialWidth) / 4)
        self.style.configure('TNotebook.Tab', 
                             padding=(self.TAB_PAD + extraPadding, 0, 
                                      self.TAB_PAD + extraPadding, 0))
        self.style.map('TNotebook.Tab', padding=[('selected', 
                                     (self.TAB_PAD + extraPadding, 0, 
                                      self.TAB_PAD + extraPadding, 0))])
        

if __name__ == '__main__':
    dbpath = os.path.abspath('dict.db')
    vfdir = os.path.abspath('demo_videofiles')
    imgdir = os.path.abspath('demo_images')
    
    Dictionary(dbpath, vfdir, imgdir).root.mainloop()
    
        
