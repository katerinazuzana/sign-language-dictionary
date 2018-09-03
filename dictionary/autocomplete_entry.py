# This module is based on:
# https://github.com/Coal0/Utilities/tree/master/tkinter_autocomplete
# where several changes and additions have been made.


try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    # Python 2
    import Tkinter as tk
    import ttk

__all__ = ["AutocompleteEntry"]

NO_RESULTS_MESSAGE = "No results found for '{}'"


class AutocompleteEntry(tk.Frame, object):
    """A container for `tk.Entry` and `tk.Listbox` widgets.
    An instance of AutocompleteEntry is actually a `tk.Frame`,
    containing the `tk.Entry` and `tk.Listbox` widgets needed
    to display autocompletion entries. Thus, you can initialize
    it with the usual arguments to `tk.Frame`.
    Constants:
    LISTBOX_HEIGHT -- Default height for the `tk.Listbox` widget
    LISTBOX_WIDTH -- Default width for the `tk.Listbox` widget
    ENTRY_WIDTH -- Default width for the `tk.Entry` widget
    Methods:
    __init__ -- Set up the `tk.Listbox` and `tk.Entry` widgets
    build -- Build a list of autocompletion entries
    update_autocomplete
    _select_entry -- Internal method
    _focus_on_listbox -- Internal method
    _focus_on_entry -- Internal method
    Other attributes:
    text -- StringVar object associated with the `tk.Entry` widget
    entry -- The `tk.Entry` widget (access this directly if you
             need to change styling)
    listbox -- The `tk.Listbox` widget (access this directly if
             you need to change styling)
    """
    LISTBOX_HEIGHT = 5
    LISTBOX_WIDTH = 25
    ENTRY_WIDTH = 25

    def __init__(self, parent, *args, **kwargs):
        """Constructor.
        Create the `self.entry` and `self.listbox` widgets.
        Note that these widgets are not yet displayed and will only
        be visible when you call `self.build`.
        Arguments:
        parent -- The parent tkinter widget
        Returns:
        None
        """
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.text = tk.StringVar()
        self.entry = tk.Entry(
            self,
            textvariable=self.text,
            width=self.ENTRY_WIDTH
        )
        self.listbox = tk.Listbox(
            self,
            height=self.LISTBOX_HEIGHT,
            width=self.LISTBOX_WIDTH
        )

    def build(
              self,
              entries,
              max_entries=5,
              case_sensitive=False,
              no_results_message=NO_RESULTS_MESSAGE
            ):
        """Set up the autocompletion settings.
        Binds <KeyRelease>, <<ListboxSelect>>, <Down> and <Up> for
        smooth cycling between autocompletion entries.
        Arguments:
        entries -- An iterable containg autocompletion entries (strings)
        max_entries -- [int] The maximum number of entries to display
        case_sensitive -- [bool] Set to `True` to make autocompletion
                          case-sensitive
        no_results_message -- [str] Message to display when no entries
                              match the current entry; you can use a
                              formatting identifier '{}' which will be
                              replaced with the entry at runtime
        Returns:
        None
        """
        if not case_sensitive:
            entries = [entry.lower() for entry in entries]

        self._case_sensitive = case_sensitive
        self._entries = entries
        self._no_results_message = no_results_message
        self._listbox_height = max_entries

        self.entry.bind("<Key>", self.update_autocomplete)
        self.entry.bind("<Down>", self._focus_on_listbox)
        self.entry.focus()
        self.entry.grid(column=0, row=0, sticky=tk.E+tk.W)
        self.columnconfigure(0, weight=1)
        
        self.listbox.bind("<<ListboxSelect>>", self._select_entry)
        self.listbox.bind("<Up>", self._focus_on_entry)
        self.listbox.grid(column=0, row=1, sticky=tk.E+tk.W+tk.N)
        self.listbox.grid_forget()
        # Initially, the listbox widget doesn't show up.

    def update_autocomplete(self, event):
        """Update `self.listbox` to display new matches.
        """
        if event.char != '':        
            self.listbox.delete(0, tk.END)
            self.listbox["height"] = self._listbox_height

            text = self.text.get()
            if not self._case_sensitive:
                text = text.lower()
            if not text:
                self.listbox.grid_forget()
            else:
                for entry in self._entries:
                    if text in entry.strip():
                        self.listbox.insert(tk.END, entry)

            listbox_size = self.listbox.size()
            if not listbox_size:
                if self._no_results_message is None:
                    self.listbox.grid_forget()
                else:
                    try:
                        self.listbox.insert(
                            tk.END,
                            self._no_results_message.format(text)
                        )
                    except UnicodeEncodeError:
                        self.listbox.insert(
                            tk.END,
                            self._no_results_message.format(
                                text.encode("utf-8")
                            )
                       )
                    if listbox_size <= self.listbox["height"]:
                        # In case there's less entries than the maximum
                        # amount of entries allowed, resize the listbox.
                        self.listbox["height"] = listbox_size
                    self.listbox.grid(sticky=tk.E+tk.W)
            else:
                if listbox_size <= self.listbox["height"]:
                    self.listbox["height"] = listbox_size
                self.listbox.grid(sticky=tk.E+tk.W)

    def _select_entry(self, event):
        """Internal method.
        Set the textvariable corresponding to `self.entry`
        to the value currently selected.
        """
        widget = event.widget
        if widget.curselection() != ():
            value = widget.get(int(widget.curselection()[0]))
            self.text.set(value)
        
    def _focus_on_listbox(self, event):
        """Internal method.
        Set focus on 'self.listbox' and select the first item.
        """
        self.listbox.selection_set(0)
        self.listbox.focus_set()
        self.listbox.event_generate("<<ListboxSelect>>")
    
    def _focus_on_entry(self, event):
        """Internal method.
        If the current selection at 'self.listbox' is the top one,
        set focus on 'self.entry'.
        """
        if self.listbox.curselection()[0] == 0:
            self.entry.focus_set()
            self.entry.icursor(tk.END)


