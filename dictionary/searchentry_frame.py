import tkinter as tk
import os
import sqlite3
from autocomplete_entry import AutocompleteEntry
import tools


class EntFrm(tk.Frame):
    """A frame with an entry and a search button."""

    def __init__(self, parent, dbpath, imgdir, searchfcn, showresultfcn,
                 **options):
        """Create an AutocompleteEntry and a Search button.

        Arguments:
            parent: a parent tkinter widget
            dbpath (str): the database file path
            searchfcn: function that does the search, takes one (str) argument
            showresultfcn: function that displays the search result,
                takes a 2-tuple argument: (boolean-flag, a-list)
        """
        super().__init__(parent, **options)
        self.dbpath = dbpath
        self.searchFcn = searchfcn
        self.showResultFcn = showresultfcn
        self.bgcolor = options.get('bg', self['bg'])
        self.defaultText = 'Zadejte výraz'
        self.iconPath = os.path.join(imgdir, 'search_icon.png')
        self.iconSize = 22
        self.makeWidgets()

    def makeWidgets(self):
        """Create the widgets."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # create the search button
        bfrm = tk.Frame(self, height=28, width=50)
        bfrm.grid_propagate(0)  # size of child doesn't affect size of parent
        bfrm.grid(column=1, row=0, sticky=tk.N)
        bfrm.rowconfigure(0, weight=1)
        bfrm.columnconfigure(0, weight=1)

        self.iconImg = tools.getImage(self.iconPath,
                                      width=self.iconSize,
                                      height=self.iconSize)
        tk.Button(bfrm,
                  image=self.iconImg,
                  command=self.doSearch,
                  bg=self.bgcolor,
                  activebackground='ghost white',
                  borderwidth=0).grid(column=0, row=0,
                                      sticky=tk.N+tk.E+tk.S+tk.W)

        # create a list of all the words contained in the database
        with sqlite3.connect(self.dbpath) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT word FROM words')
            allwords = cursor.fetchall()
        entries = tools.listOfTuplesToList(allwords)
        # The items of 'entries' will be used in AutocompleteEntry's listbox.
        # In a listbox, there's no option of inner padding, hence
        # to simmulate the padding on the left side,
        # add a space at the begining of each line.
        entries = tools.leftPadItems(entries)

        # create the autocomplete entry
        self.var = tk.StringVar()
        self.var.set(self.defaultText)
        self.ent = AutocompleteEntry(self,
                                     entries,
                                     self.defaultText,
                                     self.doSearch,
                                     maxEntries=10,
                                     textvariable=self.var)
        self.ent.grid(column=0, row=0, sticky=tk.N+tk.E+tk.W, ipady=2)
        self.ent.config(style="Gray.TEntry")

    def doSearch(self, event=None):
        """Hide listbox and do the search if there's some text in the entry."""
        if self.var.get() in ('', self.defaultText):
            # user didn't enter any text, prompt them to enter an expression
            self.master.showEnterText()
        else:
            self.ent.hideListboxWin()
            self.ent.focus_set()
            self.ent.icursor(tk.END)
            result = self.searchFcn(self.var.get())
            self.showResultFcn(result)
