from tkinter import *
from tkinter import ttk
import os
from PIL import Image, ImageTk
from scrolled_frame import ScrolledFrame

class ShapeSelectFrm(Frame):
    def __init__(self, parent, imgdir, bgcolor, **options):
        super().__init__(parent, bg=bgcolor)
        self.imgdir = imgdir
        self.bgcolor = bgcolor
        
        self.labwidth = 65
        self.labheight = 80
        self.labborder = 3
        self.numcols = 6
        self.numrows = 4
        self.sepcolor = 'gray'
        self.sepwidth = 1
        self.images = []
        self.labels = []
        
        self.shapes = [i+1 for i in range(51)]
                
        self.title = 'Tvar aktivní ruky'
        self.popuptext = 'Zvolte tvar aktivní ruky'
        
        self.var = IntVar()
        self.var.set(0)
        self.var1 = IntVar()
        self.var1.set(0)
        self.var2 = IntVar()
        self.var2.set(0)
        
        self.selectWin = None
        self.sel1 = None
        self.sep = None
        self.sel2 = None
              
        self.makeLabel()
        self.makeSelectionFrm()
        self.makeButtons()
    
    def makeLabel(self):
        Label(self, 
              text=self.title, 
              bg=self.bgcolor
              ).grid(column=0, row=0, columnspan=2, sticky=W, pady=(20, 3))
        
    def makeSelectionFrm(self):
        selfrmwidth = 2*self.labwidth + 4*self.labborder + self.sepwidth + 2*2
        selfrmheight = self.labheight + 2*self.labborder + 2*2 # 2*borderwidth
            
        self.selectionfrm = Frame(self, 
                            width=selfrmwidth, 
                            height=selfrmheight, 
                            bg=self.bgcolor, 
                            borderwidth=2, 
                            relief='groove')
        self.selectionfrm.grid(column=0, row=1, rowspan=2)
        self.selectionfrm.columnconfigure(0, 
                          minsize = self.labwidth + 2 * self.labborder)
        self.selectionfrm.rowconfigure(0, 
                          minsize = self.labheight + 2 * self.labborder)
        
        self.selectionfrm.columnconfigure(1, minsize = self.sepwidth)
        self.selectionfrm.columnconfigure(2, 
                                   minsize = self.labwidth + 2 * self.labborder)
        # Create a separator. On creation, it's not visible.
        # (It has the same color as selectionfrm background.)
        self.sep = Frame(self.selectionfrm, bg=self.bgcolor)
        self.sep.grid(column=1, row=0, sticky=N+S)
        
    def makeButtons(self):    
        self.selectBut = Button(self, text='Vybrat', command=self.openPopup)
        self.selectBut.grid(column=1, row=1, sticky=E+W, padx=20)
        
        self.delBut = Button(self, text='Zrušit', command=self.onDelete)
        self.delBut.grid(column=1, row=2, sticky=E+W, padx=20)
    
    def onDelete(self):
        if self.var2.get() != 0:
            self.var2.set(0)
        elif self.var1.get() != 0:
            self.var1.set(0)
        self.redrawSelectionFrm()
    
    def openPopup(self):
        if not self.selectWin:
            self.createPopup()
    
    def onPopupClose(self):
        self.selectWin.destroy() # deletes window from display
        self.selectWin = None
    
    def createPopup(self):
        # create a popup window
        self.selectWin = Toplevel()
        self.selectWin.title(self.title)
        self.selectWin.columnconfigure(0, weight=1)
        
        self.selectWin.protocol('WM_DELETE_WINDOW', self.onPopupClose)
        self.selectWin.attributes('-topmost', True)
        
        # set the instructions label
        Label(self.selectWin, 
              text=self.popuptext).grid(column=0, row=0, 
                                        padx=10, pady=10, 
                                        sticky=W)
        
        # make a scrolled frame for displaying labels with images
        self.scrollfrm = ScrolledFrame(self.selectWin, 
                             self.numcols*(self.labwidth + 2*self.labborder) + 
                             (self.numcols-1)*self.sepwidth,
                              
                             self.numrows*(self.labheight + 2*self.labborder) + 
                             (self.numrows-1)*self.sepwidth)
        self.scrollfrm.grid(column=0, row=1, padx=10)
        self.selectWin.rowconfigure(1, weight=1)
        
        self.makeLabels()
        
        # make Submit and Quit buttons in their own frame
        buttonsfrm = Frame(self.selectWin)
        buttonsfrm.grid(column=0, row=2, sticky=E)
        Button(buttonsfrm, 
               text='Použít', 
               command=self.onSubmit).grid(column=0, row=0, 
                                      sticky=E+W, 
                                      padx=(0, 15), pady=10)
        Button(buttonsfrm, 
               text='Zavřít', 
               command=self.onPopupClose).grid(column=1, row=0, 
                                          sticky=E+W, 
                                          padx=(0, 15), pady=10)
        
        # position the popup next to a shape selection frame
        self.selectWin.update_idletasks()
        width = self.selectWin.winfo_reqwidth()
        height = self.selectWin.winfo_reqheight()
        xoffset = self.winfo_rootx() - width
        yoffset = self.winfo_rooty() # winfo_root[x|y] returns a coord relative
                                     # to the screen's upper left corner
        self.selectWin.geometry('+{}+{}'.format(xoffset, yoffset))
        
        # disable enlarging the popup window
        self.selectWin.maxsize(width = width, height = height)
    
    def onSubmit(self):
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
        self.redrawSeparator()
        self.redrawPlace1()
        self.redrawPlace2()
        
    def redrawPlace1(self):    
        if self.var1.get() != 0:
            image = self.images[self.var1.get() - 1]    
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
        if self.var1.get() != 0:
#            self.sep = ttk.Separator(self.selectionfrm, 
#                          orient='vertical')
#            self.sep = Frame(self.selectionfrm, bg=self.sepcolor)
#            self.sep.grid(column=1, row=0, sticky=N+S)
            self.sep.configure(bg=self.sepcolor) # make the separator visible
        elif self.sel1 != None:
#            self.sep.destroy()
#            self.sep = None
            self.sep.configure(bg=self.bgcolor)  # make the separator invisible

    def redrawPlace2(self):                
        if self.var2.get() != 0:
            image = self.images[self.var2.get() - 1]
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
        if self.labels != []:
            self.labels = []
        if self.images == []:
            # create the images
            for i in self.shapes:
                imgpath = os.path.join(self.imgdir, self.num(i) + '.png')
                with Image.open(imgpath) as img:
            
                    # resize the image
                    #width, height = img.size
                    #self.labheight = int(height * self.labwidth / width)
                    img = img.resize((self.labwidth, self.labheight), 
                                     Image.LANCZOS)
                    self.images.append(ImageTk.PhotoImage(img))
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
            
            # on label click
            def clickHandler(i):
                return lambda event: self.onLabClick(i)            
            lab.bind('<Button-1>', clickHandler(i))
            
            # on label double-click
            def doubleClickHandler(i):
                return lambda event: self.onLabDoubleClick(i)            
            lab.bind('<Double-Button-1>', doubleClickHandler(i))
            
            # when the mouse cursor enters a label,
            # 
            def enterHandler(i):
                return lambda event: self.onLabEnter(i)
            lab.bind('<Enter>', enterHandler(i))
            
            # when the mouse cursor leaves a label,
            # 
            def leaveHandler(i):
                return lambda event: self.onLabLeave(i)
            lab.bind('<Leave>', leaveHandler(i))
                        
        self.createSeparators()
        
    def createSeparators(self):        
        # create vertical separators between the labels
        for i in range(self.numcols - 1):
#            sep = ttk.Separator(self.scrollfrm.interior, orient='vertical')
            sep = Frame(self.scrollfrm.interior, bg=self.sepcolor)
            sep.grid(column=2*i + 1, 
                   row=0, 
                   rowspan=(len(self.shapes)//self.numcols)*2 + 1, # num of rows
                     sticky=N+S)
        # create horizontal separators between the labels
        for i in range(len(self.shapes) // self.numcols): # number of full rows
#            sep = ttk.Separator(self.scrollfrm.interior, orient='horizontal')
            sep = Frame(self.scrollfrm.interior, bg=self.sepcolor)
            sep.grid(column=0, 
                     row=2*i + 1, 
                     columnspan=(self.numcols - 1)*2 + 1,  # num of cols
                     sticky=E+W)
        
    def onLabClick(self, i):
        # remove highlighting from the previously selected label
        if self.var.get() != 0:
            j = self.var.get() - 1
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
        self.var.set(i+1)
    
    def onLabDoubleClick(self, i):
        self.onLabClick(i)
        self.onSubmit()
                
    def onLabEnter(self, i):
        # highlight the label in blue
        if self.var.get() != i+1:
            self.labels[i].config(highlightthickness=self.labborder, 
                              highlightbackground='LightBlue1')
            self.labels[i].grid(column=(i % self.numcols) * 2, 
                                row=(i // self.numcols) * 2,
                                padx=0, pady=0)
        
    def onLabLeave(self, i):
        # remove the blue highlighting
        if self.var.get() != i+1:
            self.labels[i].config(highlightthickness=0)
            self.labels[i].grid(column=(i % self.numcols) * 2, 
                                row=(i // self.numcols) * 2,
                                padx=self.labborder, 
                                pady=self.labborder)
        
    def num(self, i):
        if i < 10: return '0' + str(i)
        return str(i)


class PassiveShapeSelectFrm(ShapeSelectFrm):
    def __init__(self, parent, imgdir, bgcolor, **options):
        super().__init__(parent, imgdir, bgcolor, **options)
         
        self.shapes = [1, 2, 4, 6, 9, 12, 13, 14, 16, 17, 23, 28, 41]
        self.numrows = 3
        
        self.title = 'Tvar pasivní ruky'
        self.popuptext = 'Zvolte tvar pasivní ruky'
    
    def makeLabel(self):
        pass
    
    def makeSelectionFrm(self):
        selfrmwidth = self.labwidth + 2*self.labborder + 2*2
        selfrmheight = self.labheight + 2*self.labborder + 2*2 
           
        self.selectionfrm = Frame(self, 
                            width=selfrmwidth, 
                            height=selfrmheight, 
                            bg=self.bgcolor, 
                            borderwidth=2, 
                            relief='groove')
        self.selectionfrm.grid(column=0, row=0, rowspan=2)
        self.selectionfrm.columnconfigure(0, 
                          minsize = self.labwidth + 2 * self.labborder)
        self.selectionfrm.rowconfigure(0, 
                          minsize = self.labheight + 2 * self.labborder)
    
    def makeButtons(self):  
        # differs from ShapeSelectFrm in row numbers  
        self.selectBut = Button(self, text='Vybrat', command=self.openPopup)
        self.selectBut.grid(column=1, row=0, sticky=E+W, padx=20)
        
        self.delBut = Button(self, text='Zrušit', command=self.onDelete)
        self.delBut.grid(column=1, row=1, sticky=E+W, padx=20)
    
    def onSubmit(self):
        if self.var.get() != 0:
            self.var1.set(self.var.get())
            self.redrawSelectionFrm()
    
    def redrawSelectionFrm(self):        
        self.redrawPlace1()
        
    def deactivate(self):
        self.selectBut.config(state='disabled')
        self.delBut.config(state='disabled')        
        
        self.darkscreen = Label(self.selectionfrm, 
                                bg='grey90', 
                                borderwidth=0)
        self.darkscreen.grid(column=0, row=0, 
                             padx=self.labborder, 
                             pady=self.labborder, 
                             sticky=N+E+S+W)
        
    def activate(self):
        self.selectBut.config(state='normal')
        self.delBut.config(state='normal')
        self.darkscreen.destroy()






