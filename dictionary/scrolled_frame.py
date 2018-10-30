import tkinter as tk
from tkinter import ttk
from autoscrollbar import AutoScrollbar


class ScrolledFrame(tk.Frame):
    """A frame that is either horizontally or vertically scrollable."""

    def __init__(self, parent, width, height, orient, border=False, **options):
        """Create a frame with a scrolled canvas that has an inner frame.

        The canvas can be scrolled using a scrollbar or by a mouse wheel.

        Arguments:
            parent: a parent tkinter widget
            width (int): a width of the visible canvas area
            height (int): a height of the visible canvas area
            orient (str): takes either 'horizontal' or 'vertical' value to
                indicate the orientation of the scrollbar
            border (bool): says whether there is a border around ScrolledFrame
        """
        super().__init__(parent, **options)
        if border:
            self.configure(borderwidth=2, relief='groove')
        bgcolor = options.get('bg', self['bg'])

        # make a canvas with vertical and horizontal scrollbars
        vsbar = AutoScrollbar(self, orient=tk.VERTICAL)
        hsbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        # AutoScrollbar doesn't work here - wouldn't appear
        # (horizontal ScrolledFrame is used with .grid_propagate(0))

        canvas = tk.Canvas(self,
                           # visible area size:
                           width=width,
                           height=height,
                           bg=bgcolor)
        vsbar.config(command=canvas.yview)
        hsbar.config(command=canvas.xview)

        if orient == 'horizontal':
            self.rowconfigure(0, minsize=height)
            self.rowconfigure(1, minsize=40)  # to fit a scrollbar
            canvas.config(xscrollcommand=hsbar.set)
            canvas.grid(column=0, row=0, sticky=tk.N+tk.S+tk.W, columnspan=3)

        else:   # vertical:
            canvas.config(yscrollcommand=vsbar.set)
            canvas.grid(column=0, row=0, sticky=tk.N+tk.E+tk.S+tk.W)
            # enable scrolling the canvas with the mouse wheel
            self.bind('<Enter>', self.bindToWheelVertical)
            self.bind('<Leave>', self.unbindWheel)

        self.rowconfigure(0, weight=1)
        canvas.config(highlightthickness=0)
        self.canvas = canvas

        # make the inner frame
        interior = tk.Frame(canvas,
                            bg=bgcolor,
                            cursor='hand2')
        self.interior = interior
        self.canvas.create_window((0, 0),
                                  window=interior,
                                  anchor=tk.NW)

        def configureInterior(event):
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            # set the total canvas size
            canvas.config(scrollregion=(0, 0, size[0], size[1]))

            if orient == 'horizontal':
                # hide scrollbar when not needed
                if interior.winfo_reqwidth() <= canvas.winfo_width():
                    hsbar.grid_forget()
                    # disable scrolling the canvas with the mouse wheel
                    self.unbind('<Enter>')
                    self.canvas.unbind('<Leave>')
                else:
                    hsbar.grid(column=0, row=1,
                               sticky=tk.N+tk.E+tk.W,
                               columnspan=3)
                    # enable scrolling the canvas with the mouse wheel
                    self.bind('<Enter>', self.bindToWheelHorizontal)
                    self.bind('<Leave>', self.unbindWheel)

        interior.bind('<Configure>', configureInterior)

    def bindToWheelVertical(self, event):
        """Bind vertical scrolling of the canvas to the mouse wheel."""
        self.canvas.bind_all('<Button-5>', self.scrollDown)
        self.canvas.bind_all('<Button-4>', self.scrollUp)

    def bindToWheelHorizontal(self, event):
        """Bind horizontal scrolling of the canvas to the mouse wheel."""
        self.canvas.bind_all('<Button-5>', self.scrollRight)
        self.canvas.bind_all('<Button-4>', self.scrollLeft)

    def unbindWheel(self, event):
        """Unbind the mouse wheel events."""
        self.canvas.unbind_all('<Button-5>')
        self.canvas.unbind_all('<Button-4>')

    def scrollDown(self, event):
        """Scroll the canvas down."""
        self.canvas.yview_scroll(1, 'units')

    def scrollUp(self, event):
        """Scroll the canvas up."""
        self.canvas.yview_scroll(-1, 'units')

    def scrollRight(self, event):
        """Scroll the canvas to the right."""
        self.canvas.xview_scroll(1, 'units')

    def scrollLeft(self, event):
        """Scroll the canvas to the left."""
        self.canvas.xview_scroll(-1, 'units')
