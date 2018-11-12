import tkinter as tk
from tkinter import ttk
from scrolledlist_frame import ScrolledList


class CatFrm(tk.Frame):
    """A frame where a word for translation might be selected from
    a category or a subcategory of words.

    Contains widgets:
    'self.catcb' combobox for choosing a category,
    'self.subcatcb' combobox for choosing one of the category's subcategories,
    'self.scrolledlist' displaying the words from the choosen (sub)category.

    The user selects the word to be translated from the scrolled list, then
    a function is called to find and display the sign language translation.
    """

    def __init__(self, parent, searchEng, showresultfcn, **options):
        """Create the frame with the comboboxes and the scrolled list.

        Arguments:
            parent: the parent tkinter widget
            searchEng: an object providing the search operations
            showresultfcn: function that displays the search result,
                takes a 2-tuple argument: (boolean-flag, a-list)
        """
        super().__init__(parent, **options)
        self.showResultFcn = showresultfcn
        self.width = 31
        self.height = 14   # scrolled list height in lines
        self.verticalSpace = 40   # space between widgets
        self.topSpace = 10   # additional padding at the top of the frame
        
        self.searchEng = searchEng
        self.makeWidgets()

    def makeWidgets(self):
        """Create a combobox for choosing a category, a combobox for choosing
        a subcategory, and a scrolled list for choosing a word.
        """
        self.columnconfigure(0, weight=1)  # empty column
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=2)  # empty column

        # empty rows:
        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(6, weight=3)

        # create category combobox
        self.catvar = tk.StringVar()
        self.catvar.set(' -- Zvolte kategorii --')
        self.catcb = ttk.Combobox(self,
                                  textvariable=self.catvar,
                                  width=self.width,
                                  state='readonly')

        # set up the options available in category combobox
        self.catcb['values'] = self.searchEng.findCats()

        self.catcb.bind('<<ComboboxSelected>>', self.catHandler)
        self.catcb.grid(column=1, row=1,
                        sticky=tk.N+tk.E+tk.S+tk.W,
                        pady=(self.topSpace, self.verticalSpace))

        # create subcategory combobox, initially disabled
        self.subcatvar = tk.StringVar()
        self.subcatvar.set(' -- Zvolte podkategorii --')
        self.subcatcb = ttk.Combobox(self,
                                     textvariable=self.subcatvar,
                                     state='disabled',
                                     width=self.width)

        self.subcatcb.bind('<<ComboboxSelected>>', self.subcatHandler)
        self.subcatcb.grid(column=1, row=3,
                           sticky=tk.N+tk.E+tk.S+tk.W,
                           pady=(0, self.verticalSpace))

        # create empty scrolledlist
        self.scrolledlist = ScrolledList(self,
                                         self.scrolledlistHandler,
                                         self.height)
        self.scrolledlist.grid(column=1, row=5,
                               sticky=tk.N+tk.E+tk.W,
                               pady=(0, self.verticalSpace))
        self.rowconfigure(2, weight=1)

    def catHandler(self, event):
        """Update the subcategory combobox and the scrolled list.

        Set up the options available in the subcategory combobox.
        Reset the subcategory combobox variable to its default value.
        Update the options in the scrolledlist to all words
        of the selectected category.
        """
        self.catcb.selection_clear()  # remove highlighting from the combobox
        subcats = self.searchEng.findSubcats(self.catvar)
        self.subcatcb['values'] = subcats
        self.subcatcb.config(state='readonly')
        self.subcatvar.set(' -- Zvolte podkategorii --')
        wordlist = self.searchEng.findWords(self.catvar, 'cat')
        self.scrolledlist.setOptions(wordlist)
        self.scrolledlist.treeview.yview_moveto(0)

    def subcatHandler(self, event):
        """Update the options in the scrolled list to the words
        of the selectected subcategory.
        """
        self.subcatcb.selection_clear()  # remove highlighting from combobox
        wordlist = self.searchEng.findWords(self.subcatvar, 'subcat')
        self.scrolledlist.setOptions(wordlist)
        self.scrolledlist.treeview.yview_moveto(0)

    def scrolledlistHandler(self, selection):
        """Search for the word translation and display the result."""
        result = self.searchEng.search(selection)
        self.showResultFcn(result)
