from tkinter import *
from tkinter import ttk


class AutocompleteEntry(ttk.Entry):
    """
    """

    def __init__(self, parent, entries, defaultText, startSearchFcn, 
                 maxEntries=5, caseSensitive=False, **kwargs):
        """
        """
        ttk.Entry.__init__(self, parent, **kwargs)
        self.focus()
        
        self.entries = entries
        self.maxEntries = maxEntries
        self.caseSensitive = caseSensitive
        self.var = kwargs['textvariable']
        self.defaultText = defaultText
        
        self.startSearch = startSearchFcn
        
        self.listboxWin = None
        self.listbox = None

        self.bind('<KeyRelease>', self.update)
        self.bind('<Down>', self.focusOnListbox)
        self.bind('<Return>', self.startSearch)
        
        # on mouse click in the entry, or when the user starts typing, 
        # delete the default text in the entry
        self.bind('<Button-1>', self.deleteDefaultText)
        self.bind('<KeyPress>', self.deleteDefaultText)
        # on focus out of the entry, insert the default text back
        self.bind('<FocusOut>', self.insertDefaultText)
        

    def update(self, event):
        """Update to display new matches."""
        if event.char not in ('', '\r'):
            # don't run on <Return>, arrow keys
            if self.var.get() == '':
                self.hideListboxWin()
            else:
                options = self.getOptions()
                if options:
                    if self.listboxWin == None:
                        self.createListboxWin()
                    elif self.listboxWin.state() == 'withdrawn':
                        self.showListboxWin()
                    self.listbox.delete(0, END)
                    for i, option in enumerate(options):
                        if i >= self.maxEntries: break
                        self.listbox.insert(END, option)
                    self.listbox['height'] = self.listbox.size() # shrink
                else:
                    self.hideListboxWin()

    def createListboxWin(self):
        self.listboxWin = Toplevel()
        self.listbox = Listbox(self.listboxWin, 
                               height=self.maxEntries, 
                               borderwidth=0)
        self.listboxWin.columnconfigure(0, minsize=self.winfo_width())
        self.listbox.grid(column=0, row=0, sticky=E+W)
        
        self.listboxWin.overrideredirect(True)
        self.placeListboxWin()
        
        self.listbox.bind("<<ListboxSelect>>", self.setEntry)
        self.listbox.bind("<Up>", self.focusOnEntry)
        self.listbox.bind('<Return>', self.startSearch)
        self.listbox.bind('<Double-Button>', self.startSearch)
        
        # get the main app window:
        # autocomplete entry -> search entry frm -> main frm -> root win
        root = self.master.master.master
        
        # bind listbox window movement to the main app window movement
        root.bind('<Configure>', self.placeListboxWin)
        
        # on mouse click out of listboxWin, hide it
        # (binding to <FocusOut> event on .overrideredirect(True) 
        # window doesn't work in Linux)
        root.bind('<Button-1>', self.onRootClick)
    
    def placeListboxWin(self, event=None):
        xoffset = self.winfo_rootx()
        yoffset = self.winfo_rooty() + self.winfo_height() - 1
        self.listboxWin.geometry('+{}+{}'.format(xoffset, yoffset))
    
    def showListboxWin(self):
        self.placeListboxWin()
        self.listboxWin.deiconify()
    
    def hideListboxWin(self, event=None):
        """Hide the listbox window if present."""
        if self.listboxWin and self.listboxWin.state() == 'normal':
            self.listboxWin.withdraw()

    def setEntry(self, event):
        """Set the entry variable to the value currently selected."""
        self.var.set(self.listbox.get(ACTIVE).lstrip())
        
    def focusOnListbox(self, event):
        """Set focus on the listbox and select the first item."""
        if self.listbox:
            self.listbox.selection_set(0)
            self.listbox.focus_set()
            self.listbox.event_generate("<<ListboxSelect>>")
    
    def focusOnEntry(self, event):
        """If the current selection of the listbox is the top one,
        set focus on the entry."""
        if self.listbox.curselection()[0] == 0:
            self.focus_set()
            self.icursor(END)

    def onRootClick(self, event):
        if event.widget not in (self, self.listbox):
            self.hideListboxWin()
    
    def getOptions(self):
        return [option for option in self.entries 
                if self.match(option, self.var.get())]

    def match(self, option, entryValue):
        if not self.caseSensitive:
            option = option.lower()
            entryValue = entryValue.lower()
        return option.lstrip().startswith(entryValue)

    def deleteDefaultText(self, event):
        """Delete the default text in the entry, if present."""
        if self.var.get() == self.defaultText:
            self.var.set('')
            self.config(style="Black.TEntry")
    
    def insertDefaultText(self, event):
        """Insert the default text back into the entry, if it's empty."""
        if self.var.get() == '':
            self.var.set(self.defaultText)
            self.config(style="Gray.TEntry")

