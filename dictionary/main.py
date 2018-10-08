#######################################################################
#                                                      
# Czech Sign Language Dictionary 
#                                                      
#######################################################################


from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
import os
from search_engine import SearchEngine
from main_frame import MainFrm
from categories_frame import CatFrm
from sign_input_frame import SignInputFrm


class Dictionary():
    """A Czech Sign Language Dictionary application.
            
    Constants:
    BORDER -- the main frame border
    WIN_MIN_WIDTH -- minimal width of the main application window
    WIN_MIN_HEIGHT -- minimal height of the main application window
    TAB_PAD -- initial notebook's tab padding
    BGCOLOR -- background color
    """

    BORDER = 38
    WIN_MIN_WIDTH = 1012
    WIN_MIN_HEIGHT = 670
    TAB_PAD = 22
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
        self.canvasSize = (250, 250)
        
        # the SearchEngine object provides the logic behind the dictionary app
        self.searchEng = SearchEngine(self.dbpath, 
                                      self.vfdir, 
                                      self.altsmax, 
                                      self.canvasSize)
        self.makeWidgets()
        
    def makeWidgets(self):
        # build the application window
        self.root = Tk()
        self.root.title('Slovník českého znakového jazyka')
        self.root.config(bg=self.BGCOLOR)
        self.root.minsize(width = self.WIN_MIN_WIDTH, 
                          height = self.WIN_MIN_HEIGHT)
        
        self.font = tkFont.Font(family='Nimbus Sans L', size=12)
        self.root.option_add('*Font', self.font)
        
        self.root.columnconfigure(0, weight=2)  # empty column
        self.root.columnconfigure(2, weight=1)  # empty column
        self.root.columnconfigure(3, weight=3)  # notebook column
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
        self.mainfrm.grid(column=1, row=0, sticky=N+E+S+W)
        
        # when the searchEng is done searching, it calls a function to show
        # the result - this function is defined in the mainfrm object
        self.searchEng.showResultFcn = self.mainfrm.showResult
        
        # create notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(column=3, row=0, sticky=N+E+S+W)
        
        # style settings
        self.style = style = ttk.Style()
        style.theme_use('clearlooks')
        
        style.configure('Gray.TEntry', foreground='gray')   # for default text
        style.configure('Black.TEntry', foreground='black') # for user input
        
        style.configure('TCombobox', background=self.BGCOLOR)
        style.map('TCombobox', background=[('disabled', self.BGCOLOR)])
        
        style.configure('Treeview', background=self.BGCOLOR, 
                                    rowheight=25, 
                                    padding=(0, 0, 0, 25))
                                    # the bottom padding is necessary for the
                                    # treeview bottom border to be visible
        style.map('Treeview', background=[('selected', 'lightgrey')])
        style.configure('Treeview.Item', padding=(-15, 0, 0, 0))
        
        # ged rid of dashed rectangle around the highlighted item in treeview
        style.layout('Treeview.Item',
          [('Treeitem.padding', {'sticky': 'nswe', 'children': 
            [('Treeitem.indicator', {'side': 'left', 'sticky': ''}),
             ('Treeitem.image', {'side': 'left', 'sticky': ''}),
            #('Treeitem.focus', {'side': 'left', 'sticky': '', 'children': [
               ('Treeitem.text', {'side': 'left', 'sticky': ''}),
            #]})
            ],
          })]
        )
        
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
        self.catfrm = CatFrm(self.notebook, 
                             self.dbpath, 
                             self.searchEng.search, 
                             bg=self.BGCOLOR, 
                             padx=self.BORDER, 
                             pady=self.BORDER)
        self.catfrm.grid(column=0, row=0, sticky=N+E+S+W)
        self.notebook.add(self.catfrm, text='Výběr podle kategorií')
        
        # create the sign-input frame
        self.signfrm = SignInputFrm(self.notebook,  
                                    self.imgdir, 
                                    self.searchEng.signSearch, 
                                    self.canvasSize, 
                                    bg=self.BGCOLOR, 
                                    padx=self.BORDER, 
                                    pady=20)
        self.signfrm.grid(column=0, row=0, sticky=N+E+S+W)
        self.notebook.add(self.signfrm, text='Překlad z ČZJ do ČJ')
        
    def positionWindow(self):
        """Position the application window in the center of the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        xOffset = self.root.winfo_screenwidth()//2 - width//2
        yOffset = self.root.winfo_screenheight()//2 - height//2
        self.root.geometry('+{}+{}'.format(xOffset, yOffset))
        
        
if __name__ == '__main__':
    dbpath = os.path.abspath('dict.db')
    vfdir = os.path.abspath('demo_videofiles')
    imgdir = os.path.abspath('demo_images')
    
    dictionary = Dictionary(dbpath, vfdir, imgdir)
    dictionary.positionWindow()
    dictionary.root.mainloop()
    
        
