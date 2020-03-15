from tkinter import *
from tkinter import filedialog as fd
import io
import pandas as pd
from factor_analyzer import *
import csv

class FormattedPrint():

    def __init__(self, PObject, Text):
        self.PObject = PObject
        self.Text = Text
        self.Output  = ''
        self.Output += str(Text) + '\n\n'
        self.Output += str(PObject) + '\n\n'

    def AppendPObject(self, PObject, Text):
        self.Output += str(Text) + '\n\n'
        self.Output += str(PObject) + '\n\n'

    def getOutput(self):
        return self.Output

class ApplicationGUI(Frame):

    def __init__(self, master, initialdir):
        super().__init__(master)
        self.filepath = StringVar()
        self._initaldir = initialdir
        self._create_widgets()
        self._display_widgets()
        self.newwin = NONE
        self.ListOfSelctedVariables = [] #selected variables for factor analysis
        self.Method=StringVar() #PCA, PAF or ML
        self.Method.set('minres')
        self.CheckboxList = [] #What needs to be displayed: Correlation matrix, Unrotated factor solutions and Scree plot
        self.FactorExtractionNumber = 1 #treshold for the extraction of factors
        self.IterationNumber = StringVar()
        self.IterationNumber.set(25) #number of iterations for extraction
        self.RotationMethod = None  #None, Varimax, Quartimax or Equimax
        self.RotationIterationNumber = StringVar()
        self.RotationIterationNumber.set(30) #rotation iteration number
        self.df = [] #Data frame
        self.printObject = FormattedPrint( '', 'FACTOR ANALYSIS')
        self.ShowCorrMatrix = 1
        self.ShowUnrotatedFS = 1
        self.ShowScreePlot = 1
        self.ShowRotatedFS = 1
        self.GutmanKaiser = BooleanVar()
        self.GutmanKaiser.set(True)
        self.ManualInput = BooleanVar()
        self.ManualInput.set(False)
        self.NumberOfFactors = StringVar()
        self.NumberOfFactors.set(0)
     #   self.SelectedVariables = [] #List of variables to be included in FA

        self._filetypes = (
            ('Comma-Separated Values', '*.csv'),
            ("All files", "*.*")
        )

    def _create_widgets(self):
        self._entry = Entry(self, textvariable=self.filepath, width=40, font=("bold", 10))
        self._button1 = Button(self, text="Učitaj...", bg="red", fg="white", command=self.browse)
        self._button2 = Button(self, text="Nastavi", bg="red", fg="white", command=self.DataWindow)
        self._label = Label(self, text="Učitaj csv fajl", fg="black", height=3,
                               font=("bold", 14))


    def _display_widgets(self):
        self._label.pack(fill='y')
        self._entry.pack(fill='x', expand=True)
        self._button1.pack(side=LEFT, fill='y')
        self._button2.pack(side=RIGHT, fill='y')

    def retrieve_input(self):
        self.filepath = self._entry.get()

    def DataWindow(self):
        self.retrieve_input()
        self.df = pd.read_csv(self.filepath)
        #print(self.newwin)
        if self.newwin != NONE:
            self.newwin.destroy()
        self.newwin = Toplevel(root)

        self.newwin.title("Faktorska analiza: Odabir varijabli")
        self.newwin.geometry("500x300")
        #label = Label(newwin, text="Faktorska analiza", fg="black", height=3, font=("bold", 14))

        frame1 = Frame(self.newwin, bg="white", width=180, height=200)
        frame1.place(x=40, y=30)
        label1 = Label(frame1, text="Postojeće varijable", bg="white", fg="black")
        label1.pack()
        scrollbar1 = Scrollbar(frame1)
        scrollbar1.pack(side=RIGHT, fill=Y)
        def SelectAllL1():
            listbox1.select_set(0, END)
            listbox1.event_generate("<<ListboxSelect>>")
        def SelectAllL2():
            listbox2.select_set(0, END)
            listbox2.event_generate("<<ListboxSelect>>")

        listbox1 = Listbox(frame1, yscrollcommand=scrollbar1.set, selectmode=EXTENDED)
        #print(self.df.iloc[0])
        for i in self.df.columns:
            listbox1.insert(END, str(i))
        listbox1.pack(side=LEFT, fill=BOTH)
        listbox1.bind("<Control-a>", lambda x: SelectAllL1())

        scrollbar1.config(command=listbox1.yview)

        frame2 = Frame(self.newwin, bg="white", width=180, height=200)
        frame2.place(x=280, y=30)
        label2 = Label(frame2, text="Odabrane varijable", bg="white", fg="black")
        label2.pack()
        scrollbar2 = Scrollbar(frame2)
        scrollbar2.pack(side=RIGHT, fill=Y)
        listbox2 = Listbox(frame2, yscrollcommand=scrollbar2.set)
        #for i in range(len(self.ListOfSelctedVariables)):
         #   listbox2.insert(END, str(i))
        listbox2.pack(side=LEFT, fill=BOTH)
        listbox2.bind("<Control-a>", lambda x: SelectAllL2())
        scrollbar2.config(command=listbox2.yview)

        if self.ListOfSelctedVariables:
            for i in range(len(self.ListOfSelctedVariables)):
                listbox2.insert(END, (self.ListOfSelctedVariables[i]))

        frame3 = Frame(self.newwin, width=200, height=50)
        frame3.place(x=160, y=250)

        backButton = Button(frame3, text="  Nazad  ", bg="red", fg="white", command=self.newwin.destroy)
        #backButton.place(x=40, y=250)
        backButton.pack(side=LEFT)

        nextButton = Button(frame3, text="Nastavi", bg="red", fg="white", command=self.ExtractionWindow)
        # backButton.place(x=40, y=250)
        nextButton.pack(side=LEFT)

        frameMiddle=Frame(self.newwin, width=58, height=40)
        frameMiddle.place(x=225, y=120)

        def ForwardVariables():
            if listbox1.curselection():
                for i in listbox1.curselection():
                    if  not (listbox1.get(i) in self.ListOfSelctedVariables):
                        listbox2.insert(END, str(listbox1.get(i)))
                        self.ListOfSelctedVariables.append(listbox1.get(i))

        def DeleteVariables():
            if listbox2.curselection():
                start = listbox2.curselection()[0]
                end = listbox2.curselection()[-1]
                for i in listbox2.curselection():
                    self.ListOfSelctedVariables.remove(listbox2.get(i))
                listbox2.delete(start,end)


        forwardButton = Button(frameMiddle, text=" > ", bg="red", fg="white", command=ForwardVariables)
        forwardButton.pack()
        deleteButton = Button(frameMiddle, text=" < ", bg="red", fg="white", command=DeleteVariables)
        deleteButton.pack()

        self.newwin.mainloop()

    def ExtractionWindow(self):

        if self.newwin != NONE:
            self.newwin.destroy()
        self.newwin = Toplevel(root)
        self.newwin.title("Faktorska analiza: Ekstrakcija")
        self.newwin.geometry("500x300")
        # label = Label(newwin, text="Faktorska analiza", fg="black", height=3, font=("bold", 14))

        frame1=Frame(self.newwin, width=500, height=300)
        frame1.pack(side=TOP)

        # Create a Tkinter variable
        tkvar = StringVar(self.newwin)

        # Dictionary with options
        choices = {'Principal Components Analysis', 'Principal Axis Factoring            ', 'Maximum Likelihood                '}
        tkvar.set('Principal Components Analysis')  # set the default option

        popupMenu = OptionMenu(frame1, tkvar, *choices)
        Label(frame1, text="Odaberi metodu:").pack(side=LEFT)
        popupMenu.pack(side=LEFT)

        # on change dropdown value
        def updateMethod(*args):
            tempMethod = tkvar.get()
            if (tempMethod == 'Minimum Residual'):
                self.Method.set('minres')
            elif (tempMethod == 'Principal Axis Factoring            '):
                self.Method.set('principal')
            elif (tempMethod == 'Maximum Likelihood                '):
                self.Method.set('ml')

        # link function to change dropdown
        tkvar.trace('w', updateMethod)

        #Reinitialize Method
        if self.Method.get() == 'minres':
            tkvar.set('Minimum Residual')
            popupMenu = OptionMenu(frame1, tkvar, *choices)
        elif self.Method.get() == 'principal':
            tkvar.set('Principal Axis Factoring            ')
            popupMenu = OptionMenu(frame1, tkvar, *choices)
        elif self.Method.get() == 'ml':
            tkvar.set('Maximum Likelihood                ')
            popupMenu = OptionMenu(frame1, tkvar, *choices)

        frame2 = Frame(self.newwin)
        frame2.pack(side=TOP)
        Label(frame2, text="Prikaži sljedeće:").grid(row=1, column=0)
        def updateSelection():
            self.ShowCorrMatrix = CorrelationMDisplay.get()
            self.ShowUnrotatedFS = UnrotatedFSDisplay.get()
            self.ShowScreePlot = ScreePlotDisplay.get()
        CorrelationMDisplay = BooleanVar()
        Button1 = Checkbutton(frame2, text="Korelaciona matrica               ",
                              variable = CorrelationMDisplay, command = updateSelection)
        Button1.grid(row=1, column=1)
        UnrotatedFSDisplay = BooleanVar()
        Button2 = Checkbutton(frame2, text="Nerotirana faktorska rješenja",
                              variable = UnrotatedFSDisplay, command = updateSelection)
        Button2.grid(row=2, column=1)
        ScreePlotDisplay = BooleanVar()
        Button3 = Checkbutton(frame2, text="Scree plot                               ",
                              variable = ScreePlotDisplay, command = updateSelection)
        Button3.grid(row=3, column=1)
        #Reinitialize checkbox
        if self.ShowCorrMatrix == 1:
            Button1.select()
        if self.ShowUnrotatedFS == 1:
            Button2.select()
        if self.ShowScreePlot == 1:
            Button3.select()

        frame3 = Frame(self.newwin)
        frame3.pack(side=TOP)
        Label(frame3, text="Faktori koji će biti ekstraktovani:").grid(row=0, column=0)

        def updateExtractionOption1(): #defining the extraction rule (eigenvalue>1)
            if self.GutmanKaiser.get():
                secondOption.deselect()
                self.NumberOfFactors = 0
                #self.ManualInput.set(False)


        def updateExtractionOption2(): #defining the extraction rule (N first values)
            if self.ManualInput.get():
                firstOption.deselect()
                #self.GutmanKaiser.set(False)

        def callback(P):  # making sure that the entry is a positive interger
            if str.isdigit(P) or P == "":
                return True
            else:
                return False

        #EigenValueCheck = BooleanVar()
        firstOption = Checkbutton(frame3, text="Gutman-Kaiser pravilo                           ",
                    variable=self.GutmanKaiser, command=updateExtractionOption1) #extract all the factors whose eigenvalue is greter than 1
        firstOption.grid(row=0, column=1)

        #ConcreteValueCheck = BooleanVar()
        secondOption = Checkbutton(frame3, text="Unos broja faktora koji će biti zadržani",
                    variable=self.ManualInput, command=updateExtractionOption2)
        secondOption.grid(row=1, column=1)

        vcmd = (frame3.register(callback))

        NumberOfFactors = Entry(frame3, validate='all', validatecommand=(vcmd, '%P'), textvariable=self.NumberOfFactors)
        NumberOfFactors.grid(row=2, column=1)

        frame4 = Frame(self.newwin)
        frame4.pack(side=TOP)
        Label(frame4, text="Broj iteracija za konvergenciju:").grid(row=0, column=0)

        IterationNumber1 = Entry(frame4, validate='all', validatecommand=(vcmd, '%P'), textvariable=self.IterationNumber)
        IterationNumber1.grid(row=0, column=1)

        frame5 = Frame(self.newwin, width=300, height=5)
        frame5.place(x=175, y=250)

        BackButton = Button(frame5, text="  Nazad ", bg="red", fg="white", command=self.DataWindow)
        BackButton.pack(side=LEFT)

        NextButton = Button(frame5, text="Nastavi", bg="red", fg="white", command=self.RotationWindow)
        NextButton.pack(side=RIGHT)

        self.newwin.mainloop()

    def RotationWindow(self):
        if self.newwin != NONE:
            self.newwin.destroy()
        self.newwin = Toplevel(root)
        self.newwin.title("Faktorska analiza: Rotacija")
        self.newwin.geometry("500x300")

        frame1 = Frame(self.newwin)
        frame1.pack(side=TOP)

        Label(frame1, text="Odaberi metodu rotacije:").pack(side=TOP)
        def updateRotationMethod1(): #settin the Rotation Method to "None"
            if RotationMethod1Check.get():
                secondOption.deselect()
                thirdOption.deselect()
                fourthOption.deselect()
                self.RotationMethod = None

        def updateRotationMethod2(): #settin the Rotation Method to "Varimax"
            if RotationMethod2Check.get():
                firstOption.deselect()
                thirdOption.deselect()
                fourthOption.deselect()
                self.RotationMethod = "varimax"

        def updateRotationMethod3(): #settin the Rotation Method to "Quartimax"
            if RotationMethod3Check.get():
                secondOption.deselect()
                firstOption.deselect()
                fourthOption.deselect()
                self.RotationMethod = "quartimax"

        def updateRotationMethod4(): #settin the Rotation Method to "Equimax"
            if RotationMethod4Check.get():
                secondOption.deselect()
                thirdOption.deselect()
                firstOption.deselect()
                self.RotationMethod = "equamax"

        RotationMethod1Check = BooleanVar()
        firstOption = Checkbutton(frame1, text="None         ",
                    variable=RotationMethod1Check, command=updateRotationMethod1)

        RotationMethod2Check = BooleanVar()
        secondOption = Checkbutton(frame1, text="Varimax   ",
                    variable=RotationMethod2Check, command=updateRotationMethod2)

        RotationMethod3Check = BooleanVar()
        thirdOption = Checkbutton(frame1, text="Quartimax",
                    variable=RotationMethod3Check, command=updateRotationMethod3)

        RotationMethod4Check = BooleanVar()
        fourthOption = Checkbutton(frame1, text="Equamax   ",
                    variable=RotationMethod4Check, command=updateRotationMethod4)

        #Reinitialize checkbox
        if self.RotationMethod == None:
            firstOption.select()
        elif self.RotationMethod == 'varimax':
            secondOption.select()
        elif self.RotationMethod == 'quartimax':
            thirdOption.select()
        elif self.RotationMethod == 'equamax':
            fourthOption.select()

        firstOption.pack(side=TOP)
        secondOption.pack(side=TOP)
        thirdOption.pack(side=TOP)
        fourthOption.pack(side=TOP)

        frame2 = Frame(self.newwin)
        frame2.place(x=150, y=120)
        Checkbutton(frame2, text="Prikaži rotirana rješenja",
                                   variable=self.ShowRotatedFS).pack()

        frame3 = Frame(self.newwin)
        frame3.place(x=80, y=150)
        Label(frame3, text="Broj iteracija za konvergenciju:").grid(row=0, column=0)

        def callback1(P):  # making sure that the entry is a positive interger
            if str.isdigit(P) or P == "":
                return True
            else:
                return False

        vcmd2 = (frame3.register(callback1))

        IterationNumber2 = Entry(frame3, validate='all', validatecommand=(vcmd2, '%P'), textvariable=self.RotationIterationNumber)
        IterationNumber2.grid(row=0, column=1)

        frame5 = Frame(self.newwin, width=300, height=5)
        frame5.place(x=175, y=250)

        BackButton = Button(frame5, text="  Nazad ", bg="red", fg="white", command=self.ExtractionWindow)
        BackButton.pack(side=LEFT)

        NextButton = Button(frame5, text="Nastavi", bg="red", fg="white", command=self.ResultsWindow)
        NextButton.pack(side=RIGHT)

        self.newwin.mainloop()

    def ResultsWindow(self):
        if self.newwin != NONE:
            self.newwin.destroy()
        self.newwin = Toplevel(root)
        self.newwin.title("Faktorska analiza: Rezultati")
        self.newwin.geometry("{0}x{1}+0+0".format(
            self.newwin.winfo_screenwidth()-3, self.newwin.winfo_screenheight()-3))
        frame1 = Frame(self.newwin, width=self.newwin.winfo_screenwidth()-300, height=self.newwin.winfo_screenheight()-300)
        frame1.pack(fill=BOTH)
        label1 = Label(frame1, text="Rezultati", fg="black")
        label1.pack(fill=BOTH)
        scrollbar1 = Scrollbar(frame1)
        scrollbar1.pack(side=RIGHT, fill=Y)

        buffer = self.FactorProcessing()

        text=Text(frame1,width=self.newwin.winfo_screenwidth()-80, height=self.newwin.winfo_screenheight()-300)
        text.insert(END, buffer)
        text.config(state=DISABLED)
        text.pack()

        frame5 = Frame(self.newwin, width=300, height=5)
        frame5.place(x=0.42*(self.newwin.winfo_screenwidth()-3), y=(self.newwin.winfo_screenheight()-3)*0.85)
        #print( self.newwin.winfo_screenwidth()-3)

        BackButton = Button(frame5, text="  Nazad ", bg="red", fg="white", command=self.RotationWindow)
        BackButton.pack(side=LEFT, fill=BOTH)

        def SaveResults():
            with open('Results.csv', 'a') as f:
                w = csv.writer(f, quoting=csv.QUOTE_ALL)
                w.writerow(text.get("1.0",END))

        SaveButton = Button(frame5, text="Sačuvaj", bg="red", fg="white", command=SaveResults)
        SaveButton.pack(side=RIGHT, fill=BOTH)

        frame6 = Frame(self.newwin, width=30, height=5)
        frame6.place(x=0.84 * (self.newwin.winfo_screenwidth() - 3), y=(self.newwin.winfo_screenheight() - 3) * 0.85)

        ExitButton = Button(frame6, text="   Izađi   ", bg="red", fg="white", command=self.newwin.destroy)
        ExitButton.pack(fill=BOTH)

        self.newwin.mainloop()

    def browse(self):

        self.filepath.set(fd.askopenfilename(initialdir=self._initaldir,
                                             filetypes=self._filetypes))

    def FactorProcessing(self):
        #Create a data frame of only selected variables
        SelectedDF = self.df[self.ListOfSelctedVariables]
        fa = FactorAnalyzer()
        fa.analyze(SelectedDF, 4, rotation=None, method=self.Method)
        rotator = Rotator()
        if (bool(self.ShowCorrMatrix)):
            self.printObject.AppendPObject(fa.corr, "Correlation matrix")
        if (bool(self.ShowUnrotatedFS)):
            self.printObject.AppendPObject(fa.loadings, "Unrotated extractes factors:")

        self.printObject.AppendPObject(fa.get_eigenvalues()[0], "Eigenvalues:")
        self.printObject.AppendPObject(fa.get_eigenvalues()[1], "New eigenvalues:")
        return self.printObject.getOutput()

if __name__ == '__main__':
    root = Tk()
    root.title("Aplikacija za faktorsku analizu podataka")
    labelfont = ('times', 10, 'bold')
    root.geometry("500x200")
    AppObject = ApplicationGUI(root, initialdir=r"/home/haris/Desktop/Teza") #r"/home"
    AppObject.pack(fill='y')

    root.mainloop()