from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
import os
from scrolled_frame import ScrolledFrame
import tools


class ShapeSelectFrm(Frame):
    """A frame for selecting one or more handshapes of the active hand.
    
    The frame contains:
    - a label with a title
    - 'self.selectionfrm' frame with two places where the selected handshapes
                          are displayed
    - 'self.addBut' - Add button that opens a popup window with
                         an offer of handshapes
    - 'self.delBut' - Delete button for deleting a handshape from selection
    """
    
    def __init__(self, parent, imgdir, **options):
        """Initialize a ShapeSelectFrm. Create 'selectionfrm' and buttons.
        
        Arguments:
            parent: a parent tkinter widget
            imgdir (str): a path to the directory with images
        """
        super().__init__(parent, **options)
        self.imgdir = imgdir
        self.bgcolor = options.get('bg', self['bg'])
        self.labPady = 3   # title label y-padding
        
        self.addIconPath = os.path.join(imgdir, 'add_icon.png')
        self.delIconPath = os.path.join(imgdir, 'del_icon.png')
        self.iconSize = 32
        self.butSize = 35
        self.butPadx = 20   # Select and Delete buttons padding
        self.butPady = 2
        self.delay = 1000 # how long to wait before button description shows up
        self.captFont = None
        self.captFontSize = 10   # font size of the captions messages
        self.msgWidth = 100      # width of the caption message widget
        
        self.submitIconPath = os.path.join(imgdir, 'submit_icon.png')
        self.closeIconPath = os.path.join(imgdir, 'close_icon.png')
        self.popupWinIconSize = 15
        
        self.labwidth = 65
        self.labheight = 80
        self.labborder = 3
        self.numcols = 6
        self.numrows = 4
        self.sepcolor = 'gray'
        self.sepwidth = 1
        
        self.images = []     # images of the handshapes
        self.labels = []     # labels with handshape pics in the popup window
        self.shapes = [i+1 for i in range(54)]
                
        self.title = 'Tvar aktivní ruky'
        self.popuptext = 'Zvolte tvar aktivní ruky'
        self.popupBgColor = '#efebe7'
        
        self.var = IntVar()  # tracks a shape selected in the popup window
        self.var.set(0)          # 0 means there's no shape selected
        self.var1 = IntVar() # tracks a shape displayed on the 1st place
        self.var1.set(0)
        self.var2 = IntVar() # tracks a shape displayed on the 2nd place
        self.var2.set(0)
        
        self.popupWin = None
        self.sel1 = None    # label with 1st selected shape
        self.sep = None     # separator-like frame separating the labels
        self.sel2 = None    # label with 2nd selected shape
        
        # popup canvas size
        self.canvasWidth = (self.numcols*(self.labwidth + 2*self.labborder) + 
                            (self.numcols-1)*self.sepwidth)
        self.canvasHeight = (self.numrows*(self.labheight + 2*self.labborder) + 
                             (self.numrows-1)*self.sepwidth)
        
        self.columnconfigure(0, weight=1)  # empty column
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)  # empty column
              
        self.makeLabel()
        self.makeSelectionFrm()
        self.makeButtons()
    
    def makeLabel(self):
        """Create a label with a title."""
        Label(self, 
              text=self.title, 
              bg=self.bgcolor
              ).grid(column=1, row=0, sticky=E+W, pady=(0, self.labPady))
              
    def makeSelectionFrm(self):
        """Create a frame where the selected shapes are displayed."""
        selfrmwidth = 2*self.labwidth + 4*self.labborder + self.sepwidth + 2*2
        selfrmheight = self.labheight + 2*self.labborder + 2*2 # 2*borderwidth
            
        self.selectionfrm = Frame(self, 
                                  width=selfrmwidth, 
                                  height=selfrmheight, 
                                  bg=self.bgcolor, 
                                  borderwidth=2, 
                                  relief='groove')
        self.selectionfrm.grid(column=1, row=1, rowspan=2, sticky=W)
        
        self.selectionfrm.columnconfigure(0, 
                                   minsize=self.labwidth + 2*self.labborder)
        self.selectionfrm.rowconfigure(0, 
                                   minsize=self.labheight + 2*self.labborder)
        self.selectionfrm.columnconfigure(1, minsize=self.sepwidth)
        self.selectionfrm.columnconfigure(2, 
                                   minsize=self.labwidth + 2*self.labborder)
        
        # Create a separator. On creation, it's not visible.
        # (It has the same color as selectionfrm background.)
        self.sep = Frame(self.selectionfrm, bg=self.bgcolor)
        self.sep.grid(column=1, row=0, sticky=N+S)
        
    def makeButtons(self):
        """Create Add and Delete buttons."""
        self.caption = None
        
        # create Add button
        self.addImg = tools.getImage(self.addIconPath, 
                                     width=self.iconSize, 
                                     height=self.iconSize)
        self.addBut = Button(self, 
                             image=self.addImg, 
                             command=self.openPopup, 
                             width=self.butSize, 
                             height=self.butSize, 
                             bg=self.bgcolor, 
                             activebackground=self.bgcolor, 
                             borderwidth=0, 
                             highlightthickness=0)
        self.addBut.grid(column=2, 
                         row=1, 
                         sticky=W+S, 
                         padx=self.butPadx, 
                         pady=self.butPady)
        
        # when mouse is over the button for a while, show a caption
        self.addBut.bind('<Enter>', lambda ev: self.onButEnter('Přidat'))
        self.addBut.bind('<Leave>', self.onButLeave)
        
        # create Delete button
        self.delImg = tools.getImage(self.delIconPath, 
                                     width=self.iconSize, 
                                     height=self.iconSize)
        self.delBut = Button(self, 
                             image=self.delImg, 
                             command=self.onDelete, 
                             width=self.butSize, 
                             height=self.butSize, 
                             bg=self.bgcolor, 
                             activebackground=self.bgcolor, 
                             borderwidth=0, 
                             highlightthickness=0)
        self.delBut.grid(column=2, 
                         row=2, 
                         sticky=W+N, 
                         padx=self.butPadx, 
                         pady=self.butPady)
        
        # when mouse is over the button for a while, show a caption
        self.delBut.bind('<Enter>', lambda ev: self.onButEnter('Odstranit'))
        self.delBut.bind('<Leave>', self.onButLeave)
    
    def onButEnter(self, text):
        """Call the after() method to show a button caption."""
        self.job = self.after(self.delay, lambda: self.showCaption(text))
    
    def onButLeave(self, event):
        """Stop showing the button caption."""
        self.after_cancel(self.job)
        if self.caption: self.hideCaption()
    
    def showCaption(self, text):
        """Create a toplevel window with a caption message."""
        self.caption = Toplevel()
        msg = Message(self.caption, 
                      text=text, 
                      width=self.msgWidth, 
                      bg=self.bgcolor)
        msg.grid()
        
        # set hint font if not defined yet
        if not self.captFont:
            font = tkFont.Font(font=msg['font'])    # the application's font
            font.configure(size=self.captFontSize)
            self.captFont = font                    # caption font
        msg.config(font=self.captFont)
        
        # position the window at the right bottom of mouse cursor
        x, y = self.winfo_pointerxy()
        xoffset = x + 10 # x + approx cursor size
        yoffset = y + 11 # y + approx cursor size
        self.caption.geometry('+{}+{}'.format(xoffset, yoffset))
        self.caption.overrideredirect(True)
    
    def hideCaption(self):
        """Destroy the 'self.caption' window."""
        self.caption.destroy()
        self.caption = None  
    
    def onDelete(self):
        """Delete the rightmost one of the selected shapes."""
        if self.var2.get() != 0:
            self.var2.set(0)
        elif self.var1.get() != 0:
            self.var1.set(0)
        self.redrawSelectionFrm()
    
    def openPopup(self):
        """Open a popup window."""
        if self.popupWin:
            self.popupWin.deiconify()
        else:
            self.createPopup()
    
    def createPopup(self):
        """Create a popup window for selecting a handshape."""
        # create a popup window
        self.popupWin = Toplevel(bg=self.popupBgColor)
        self.popupWin.title(self.title)
        self.popupWin.columnconfigure(0, weight=1)
        
        self.popupWin.protocol('WM_DELETE_WINDOW', self.onPopupClose)
        self.popupWin.attributes('-topmost', True)
        
        # set the instructions label
        Label(self.popupWin, 
              text=self.popuptext, 
              bg=self.popupBgColor).grid(column=0, row=0, 
                                        padx=10, pady=10, 
                                        sticky=W)
        
        # make a scrolled frame for displaying labels with images
        self.scrollfrm = ScrolledFrame(self.popupWin, 
                                       self.canvasWidth,
                                       self.canvasHeight, 
                                       orient='vertical', 
                                       border=True, 
                                       bg=self.bgcolor)
        self.scrollfrm.grid(column=0, row=1, padx=10)
        self.popupWin.rowconfigure(1, weight=1)
        
        self.makeLabels()
        self.makePopupWinButtons()
        
        self.positionWindow()
        self.popupWin.resizable(False, False)
        
    def positionWindow(self):
        """Position the 'self.popupWin' window.
        
        Position 'self.popupWin' window slightly to the left 
        from the center of the main app window, so that the selected shapes 
        in the main window are visible.
        """
        width = self.canvasWidth
        height = self.canvasHeight
        
        # get the main application window object
        root = self.getRoot()
        
        rootWidth = root.winfo_width()
        rootHeight = root.winfo_height()
        rootX = root.winfo_rootx()
        rootY = root.winfo_rooty()
        rootCenterX = rootX + rootWidth // 2
        rootCenterY = rootY + rootHeight // 2
        
        xoffset = rootCenterX - width * 2 // 3
        yoffset = rootCenterY - height * 2 // 3
        self.popupWin.geometry('+{}+{}'.format(xoffset, yoffset))
    
    def getRoot(self):
        """Return the root application window object."""
        # actshapes -> signfrm -> notebook -> root
        root = self.master.master.master
        return root
    
    def makePopupWinButtons(self):
        """Create the Submit and Quit buttons in their own frame."""
        buttonsfrm = Frame(self.popupWin, bg=self.popupBgColor)
        buttonsfrm.grid(column=0, row=2, sticky=E)
        
        # submit button
        self.submitImg = tools.getImage(self.submitIconPath, 
                                        width=self.popupWinIconSize, 
                                        height=self.popupWinIconSize)
        submitButton = ttk.Button(buttonsfrm, 
                                  text=' Použít', 
                                  image=self.submitImg, 
                                  command=self.onSubmit)
        submitButton.grid(column=0, row=0, 
                          sticky=E+W, 
                          padx=(0, 15), pady=10)
        submitButton['compound'] = LEFT # display image to left of button text
        
        # close button
        self.closeImg = tools.getImage(self.closeIconPath, 
                                       width=self.popupWinIconSize, 
                                       height=self.popupWinIconSize)
        closeButton = ttk.Button(buttonsfrm, 
                                 text=' Zavřít', 
                                 image=self.closeImg, 
                                 command=self.onPopupClose)
        closeButton.grid(column=1, row=0, 
                         sticky=E+W, 
                         padx=(0, 15), pady=10)
        closeButton['compound'] = LEFT
    
    def onSubmit(self):
        """Update 'var1' and 'var2' variables and redraw 'selectionfrm'."""
        if self.var.get() != 0:
            selection = self.var.get()
            place1 = self.var1.get()
            place2 = self.var2.get()
            if place1 == 0:         # 1st place is empty
                self.var1.set(selection)
            elif place2 == 0:       # only 2nd place is empty
                if selection != place1:
                    self.var2.set(selection)
            else:                   # both places are occupied
                if selection != place2:
                    self.var1.set(self.var2.get()) # move 2nd to 1st
                    self.var2.set(selection)     # set 2nd to current selection
            self.redrawSelectionFrm()
    
    def redrawSelectionFrm(self):
        """Update 'self.selectionfrm' frame."""     
        self.redrawSeparator()
        self.redrawPlace1()
        self.redrawPlace2()
        
    def redrawPlace1(self):
        """Update 'self.sel1' label."""
        if self.var1.get() != 0:
            image = self.images[self.shapes.index(self.var1.get())]
            if self.sel1 != None: self.sel1.destroy()
            self.sel1 = Label(self.selectionfrm, 
                              image=image, 
                              borderwidth=0)
            self.sel1.grid(column=0, 
                           row=0,
                           padx=self.labborder, 
                           pady=self.labborder)            
        elif self.sel1 != None:
            self.sel1.destroy()
            self.sel1 = None

    def redrawSeparator(self):
        """Update the color of the separator."""
        if self.var1.get() != 0:
            self.sep.configure(bg=self.sepcolor) # make the separator visible
        elif self.sel1 != None:
            self.sep.configure(bg=self.bgcolor)  # make the separator invisible

    def redrawPlace2(self):
        """Update 'self.sel2' label."""
        if self.var2.get() != 0:
            image = self.images[self.shapes.index(self.var2.get())]
            if self.sel2 != None: self.sel2.destroy()    
            self.sel2 = Label(self.selectionfrm, 
                              image=image, 
                              borderwidth=0)
            self.sel2.grid(column=2, 
                           row=0,
                           padx=self.labborder, 
                           pady=self.labborder)
        else:
            if self.sel2 != None:
                self.sel2.destroy()
                self.sel2 = None                
        
    def makeLabels(self):
        """Fill the interior of 'self.scrollfrm' with labels."""
        # create the images if they are not created yet
        if self.images == []:
            for i in self.shapes:
                imgpath = os.path.join(self.imgdir, self.num(i) + '.png')
                image = tools.getImage(imgpath, self.labwidth, self.labheight)
                self.images.append(image)
        
        # create the labels if they are not created yet
        if self.labels == []:
            for i in range(len(self.shapes)):                
                # display the image on a label            
                lab = Label(self.scrollfrm.interior, 
                            image=self.images[i], 
                            borderwidth=0)
                lab.grid(column=(i % self.numcols) * 2, 
                         row=(i // self.numcols) * 2,
                         padx=self.labborder, 
                         pady=self.labborder)
                self.labels.append(lab)    
            
                # on label click, change the color of highlighting
                def clickHandler(i):
                    return lambda event: self.onLabClick(i)            
                lab.bind('<Button-1>', clickHandler(i))
                
                # on label double-click, the label is fetched
                def doubleClickHandler(i):
                    return lambda event: self.onLabDoubleClick(i)            
                lab.bind('<Double-Button-1>', doubleClickHandler(i))
                
                # when the cursor enters a label, the label is highlighted
                def enterHandler(i):
                    return lambda event: self.onLabEnter(i)
                lab.bind('<Enter>', enterHandler(i))
                
                # when the cursor leaves a label, highlighting is removed
                def leaveHandler(i):
                    return lambda event: self.onLabLeave(i)
                lab.bind('<Leave>', leaveHandler(i))
                            
        self.createSeparators()
        
    def createSeparators(self):
        """Create 'separators' (implemented as thin frames) between labels."""  
        # create vertical separators between the labels
        for i in range(self.numcols - 1):
            sep = Frame(self.scrollfrm.interior, bg=self.sepcolor)
            sep.grid(column=2*i + 1, 
                   row=0, 
                   rowspan=(len(self.shapes)//self.numcols)*2 + 1, # num of rows
                     sticky=N+S)
        
        # create horizontal separators between the labels
        for i in range(len(self.shapes) // self.numcols): # number of full rows
            sep = Frame(self.scrollfrm.interior, bg=self.sepcolor)
            sep.grid(column=0, 
                     row=2*i + 1, 
                     columnspan=(self.numcols - 1)*2 + 1,  # num of cols
                     sticky=E+W)
        
    def onLabClick(self, i):
        """Highlight the label in red."""
        # remove highlighting from the previously selected label
        if self.var.get() != 0:
            j = self.shapes.index(self.var.get())
            self.labels[j].config(highlightthickness=0)
            self.labels[j].grid(column=(j % self.numcols) * 2, 
                                row=(j // self.numcols) * 2,
                                padx=self.labborder, 
                                pady=self.labborder)
        # highlight the selected label
        self.labels[i].config(highlightthickness=self.labborder, 
                              highlightbackground='red')
        self.labels[i].grid(column=(i % self.numcols) * 2, 
                            row=(i // self.numcols) * 2,
                            padx=0, pady=0)
        self.var.set(self.shapes[i])
    
    def onLabDoubleClick(self, i):
        self.onLabClick(i)
        self.onSubmit()
                
    def onLabEnter(self, i):
        """Highlight the label in blue."""
        if self.var.get() == 0 or self.shapes.index(self.var.get()) != i:
            # the ith label is not selected
            self.labels[i].config(highlightthickness=self.labborder, 
                              highlightbackground='LightBlue1')
            self.labels[i].grid(column=(i % self.numcols) * 2, 
                                row=(i // self.numcols) * 2,
                                padx=0, pady=0)
        
    def onLabLeave(self, i):
        """Remove the blue highlighting from the label."""
        if self.var.get() == 0 or self.shapes.index(self.var.get()) != i:
            # the ith label is not selected
            self.labels[i].config(highlightthickness=0)
            self.labels[i].grid(column=(i % self.numcols) * 2, 
                                row=(i // self.numcols) * 2,
                                padx=self.labborder, 
                                pady=self.labborder)
        
    def num(self, i):
        """Convert (int) to (str) and if single digit, left-pad it with 0."""
        if i < 10: return '0' + str(i)
        return str(i)
    
    def onPopupClose(self):
        """Delete the window from display."""
        self.popupWin.withdraw()


class PassiveShapeSelectFrm(ShapeSelectFrm):
    """A frame for selecting a handshape of the passive hand.
    
    The frame contains:
    - 'self.selectionfrm' frame with one place where the selected handshape
                          is displayed
    - 'self.addBut' - Add button that opens a popup window with
                         an offer of handshapes
    - 'self.delBut' - Delete button for deleting the handshape from selection
    """
    
    def __init__(self, parent, imgdir, **options):
        """Initialize a PassiveShapeSelectFrm.
        
        Arguments:
            parent: a parent tkinter widget
            imgdir (str): a path to the directory with images
        """
        super().__init__(parent, imgdir, **options)
         
        self.shapes = [1, 2, 4, 6, 9, 11, 12, 13, 15, 16, 22, 29, 42]
        self.numrows = 3
        
        # popup canvas size
        self.canvasWidth = (self.numcols*(self.labwidth + 2*self.labborder) + 
                            (self.numcols-1)*self.sepwidth)
        self.canvasHeight = (self.numrows*(self.labheight + 2*self.labborder) + 
                             (self.numrows-1)*self.sepwidth)
        
        self.title = 'Tvar pasivní ruky'
        self.popuptext = 'Zvolte tvar pasivní ruky'
    
    def makeLabel(self):
        pass
    
    def makeSelectionFrm(self):
        """Create a frame where the selected shape is displayed."""
        selfrmwidth = self.labwidth + 2*self.labborder + 2*2 # 2*borderwidth
        selfrmheight = self.labheight + 2*self.labborder + 2*2 
           
        self.selectionfrm = Frame(self, 
                                  width=selfrmwidth, 
                                  height=selfrmheight, 
                                  bg=self.bgcolor, 
                                  borderwidth=2, 
                                  relief='groove')
        self.selectionfrm.grid(column=1, row=1,    # 0th row is empty
                               rowspan=2, 
                               sticky=W)
                               
        self.selectionfrm.columnconfigure(0, 
                          minsize=self.labwidth + 2*self.labborder)
        self.selectionfrm.rowconfigure(0, 
                          minsize=self.labheight + 2*self.labborder)
    
    def onSubmit(self):
        """Update 'self.var1' variable and redraw 'self.selectionfrm'."""
        if self.var.get() != 0:
            self.var1.set(self.var.get())
            self.redrawSelectionFrm()
    
    def redrawSelectionFrm(self):
        """Update 'self.selectionfrm' frame."""
        self.redrawPlace1()
    
    def getRoot(self):
        """Return the root application window object."""
        # passhapes -> radiofrm -> signfrm -> notebook -> root
        root = self.master.master.master.master
        return root
        
    def deactivate(self):
        """Disable the buttons and darken the widgets."""
        self.addBut.config(state='disabled')
        self.delBut.config(state='disabled')        
        
        self.darkscreen = Label(self.selectionfrm, 
                                bg='grey90', 
                                borderwidth=0)
        self.darkscreen.grid(column=0, row=0, 
                             padx=self.labborder, 
                             pady=self.labborder, 
                             sticky=N+E+S+W)
        
    def activate(self):
        """Reset the buttons to normal state and remove the darkening layer."""
        self.addBut.config(state='normal')
        self.delBut.config(state='normal')
        self.darkscreen.destroy()

