from tkinter import *
from shape_select_frame import PassiveShapeSelectFrm


class RadioFrm(Frame):

    def __init__(self, parent, imgdir, **options):
    
        super().__init__(parent, **options)
        self.imgdir = imgdir
        self.bgcolor = options.get('bg', self['bg'])
        self.var = StringVar()
        self.values = [('jednoruční znak', 'single hand'), 
                       ('obě ruce stejný tvar', 'both the same'), 
                       ('tvar pasivní ruky', 'passive hand')]
        self.pady = 6   # passhapes frame y-padding
        self.makeWidgets()
        
    def makeWidgets(self):
    
        self.columnconfigure(0, weight=1)   # empty column
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=3)   # empty column
        
        for i in range(len(self.values)):
            Radiobutton(self, text = self.values[i][0], 
                              variable = self.var, 
                              value = self.values[i][1], 
                              command = self.onPress, 
                              bg = self.bgcolor, 
                              activebackground = self.bgcolor, 
                              highlightthickness = 0
                              ).grid(column=1, row=i, sticky=W)
        
        self.var.set('single hand')
        self.passhapes = PassiveShapeSelectFrm(self, 
                                               self.imgdir, 
                                               bg=self.bgcolor)
        self.passhapes.grid(column=1, row=3, 
                            sticky=E+W, 
                            pady=(self.pady, 0))
        self.passhapes.deactivate()
        
    def onPress(self):
        if self.var.get() == 'passive hand':
            self.passhapes.activate()
        else:
            self.passhapes.deactivate()

