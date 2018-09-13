from tkinter import *
from tkinter import ttk


class AutocompleteEntry(ttk.Entry):
    """
    """

    def __init__(self, parent, entries, startSearchFcn, maxEntries=5, 
                 caseSensitive=False, **kwargs):
        """
        """
        ttk.Entry.__init__(self, parent, **kwargs)
        self.focus()
        
        self.entries = entries
        self.maxEntries = maxEntries
        self.caseSensitive = caseSensitive
        self.var = kwargs['textvariable']
        
        self.startSearch = startSearchFcn
        
        self.listboxWin = None
        self.listbox = None

        self.bind('<KeyRelease>', self.update)
        self.bind('<Down>', self.focusOnListbox)
        

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
        
        # window properties and placement
        self.listboxWin.overrideredirect(True)
#        self.listboxWin.attributes('-topmost', True)
        xoffset = self.winfo_rootx()
        yoffset = self.winfo_rooty() + 29
        self.listboxWin.geometry('+{}+{}'.format(xoffset, yoffset))
        
        self.listbox.bind("<<ListboxSelect>>", self.setEntry)
        self.listbox.bind("<Up>", self.focusOnEntry)
        self.listbox.bind('<Return>', self.startSearch)
        self.listbox.bind('<Double-Button>', self.startSearch)
        
        # bind listbox window movement to the main app window movement
        # autocomplete entry -> search entry frm -> main frm -> root win
        self.master.master.master.bind('<Configure>', self.drag)
    
    def drag(self, event):
        xoffset = self.winfo_rootx()
        yoffset = self.winfo_rooty() + 29
        self.listboxWin.geometry('+{}+{}'.format(xoffset, yoffset))
    
    def showListboxWin(self):
        xoffset = self.winfo_rootx()
        yoffset = self.winfo_rooty() + 29
        self.listboxWin.geometry('+{}+{}'.format(xoffset, yoffset))
        self.listboxWin.deiconify()
    
    def hideListboxWin(self):
        """Hide the listbox window if present."""
        if self.listboxWin and self.listboxWin.state() == 'normal':
            self.listboxWin.withdraw()

    def setEntry(self, event):
        """Set the textvariable corresponding to `self.entry`
        to the value currently selected."""
        self.var.set(self.listbox.get(ACTIVE).lstrip())
        
    def focusOnListbox(self, event):
        """Set focus on the listbox and select the first item."""
        self.listbox.selection_set(0)
        self.listbox.focus_set()
        self.listbox.event_generate("<<ListboxSelect>>")
    
    def focusOnEntry(self, event):
        """If the current selection of the listbox is the top one,
        set focus on the entry."""
        if self.listbox.curselection()[0] == 0:
            self.focus_set()
            self.icursor(END)

    def getOptions(self):
        return [option for option in self.entries 
                if self.match(option, self.var.get())]

    def match(self, option, entryValue):
        if not self.caseSensitive:
            option = option.lower()
            entryValue = entryValue.lower()
        return option.lstrip().startswith(entryValue)



