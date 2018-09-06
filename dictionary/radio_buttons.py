from tkinter import *
from shape_select_frame import PassiveShapeSelectFrm

class RadioFrm(Frame):
    def __init__(self, parent, imgdir, **options):
        super().__init__(parent, **options)
        self.imgdir = imgdir
        self.bgcolor = options.get('bg', self['bg'])
        self.var = StringVar()
        
        values = [('jednoruční znak', 'single hand'), 
                  ('obě ruce stejný tvar', 'both the same'), 
                  ('tvar pasivní ruky', 'passive hand')]
        
        for i in range(len(values)):
            Radiobutton(self, text=values[i][0], 
                              variable=self.var, 
                              value=values[i][1], 
                              command=self.onPress, 
                              bg=self.bgcolor, 
                              activebackground=self.bgcolor, 
                              highlightthickness=0
                              ).grid(column=0, row=i, sticky=W)
        
        self.var.set('single hand')
        
        self.passhapes = PassiveShapeSelectFrm(self, 
                                               self.imgdir, 
                                               bg=self.bgcolor)
        self.passhapes.grid(column=0, row=3, pady=(6, 0))
        self.passhapes.deactivate()
        
    def onPress(self):
        if self.var.get() == 'passive hand':
            self.passhapes.activate()
        else:
            self.passhapes.deactivate()
