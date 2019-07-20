from tkinter import *

from tkinter import filedialog as fd




class ApplicationGUI(Frame):
    """ Creates a frame that contains a button when clicked lets the user to select
    a file and put its filepath into an entry.
    """

    def __init__(self, master, initialdir='', filetypes=()):
        super().__init__(master)
        self.filepath = StringVar()
        self._initaldir = initialdir
        self._filetypes = filetypes
        self._create_widgets()
        self._display_widgets()
        self.newwin = NONE
        self.ListOfSelctedVariables=[]
        self.Method=StringVar()
        self.CheckboxList=[]
        self.FactorExtractionNumber=1
        self.IterationNumber = 0


    def _create_widgets(self):
        self._entry = Entry(self, textvariable=self.filepath, font=("bold", 10))
        self._button1 = Button(self, text="Učitaj...", bg="red", fg="white", command=self.browse)
        self._button2 = Button(self, text="Nastavi", bg="red", fg="white", command=self.DataWindow)
        self._label = Label(self, text="Učitaj csv fajl", fg="black", height=3,
                               font=("bold", 14))

    def _display_widgets(self):
        self._label.pack(fill='y')
        self._entry.pack(fill='x', expand=True)
        self._button1.pack(side=LEFT, fill='y')
        #self.retrieve_input()
        self._button2.pack(side=RIGHT, fill='y')

    def retrieve_input(self):
        self.filepath.set(self._entry.get())
        #print(self.filepath.get())

    def DataWindow(self):
        self.retrieve_input()
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

        listbox1 = Listbox(frame1, yscrollcommand=scrollbar1.set, selectmode=EXTENDED)
        for i in range(50, 1000):
            listbox1.insert(END, str(i))
        listbox1.pack(side=LEFT, fill=BOTH)

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
        scrollbar2.config(command=listbox2.yview)

        if self.ListOfSelctedVariables:
            for i in range(len(self.ListOfSelctedVariables)):
                listbox2.insert(END, (self.ListOfSelctedVariables[i]))

        frame3 = Frame(self.newwin, width=200, height=50)
        frame3.place(x=160, y=250)

        def Reinitialize():
            self.ListOfSelctedVariables = []
            self.Method = StringVar()
            self.CheckboxList = []
            self.FactorExtractionNumber = 1
            self.IterationNumber = 0
            self.newwin.destroy()

        backButton = Button(frame3, text="  Nazad  ", bg="red", fg="white", command=Reinitialize)
        #backButton.place(x=40, y=250)
        backButton.pack(side=LEFT)

        nextButton = Button(frame3, text="Nastavi", bg="red", fg="white", command=self.ExtractionWindow)
        # backButton.place(x=40, y=250)
        nextButton.pack(side=LEFT)

        frameMiddle=Frame(self.newwin, width=58, height=40)
        frameMiddle.place(x=225, y=120)

        def ForwardVariables():
            if listbox1.curselection():
                for i in range(len(listbox1.curselection())):
                    if  not (listbox1.get(listbox1.curselection()[i]) in self.ListOfSelctedVariables):
                        listbox2.insert(END, str(listbox1.get(listbox1.curselection()[i])))
                        self.ListOfSelctedVariables.append(listbox1.get(listbox1.curselection()[i]))


        def DeleteVariables():
            if listbox2.curselection():
                self.ListOfSelctedVariables.remove(listbox2.get(listbox2.curselection()))
                listbox2.delete(listbox2.curselection())

        forwardButton = Button(frameMiddle, text=" > ", bg="red", fg="white", command=ForwardVariables)
        forwardButton.pack()
        deleteButton = Button(frameMiddle, text=" < ", bg="red", fg="white", command=DeleteVariables)
        deleteButton.pack()
        #print(listbox1.get(0,1))

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
            self.Method.set(tkvar.get())


        # link function to change dropdown
        tkvar.trace('w', updateMethod)

        frame2 = Frame(self.newwin)
        frame2.pack(side=TOP)
        Label(frame2, text="Prikaži sljedeće:").grid(row=1, column=0)

        CorrelationMDisplay = BooleanVar()
        Checkbutton(frame2, text="Korelaciona matrica               ", variable=CorrelationMDisplay).grid(row=1, column=1)
        #print(CorrelationMDisplay.get())
        UnrotatedFSDisplay = BooleanVar()
        Checkbutton(frame2, text="Nerotirana faktorska rješenja", variable=UnrotatedFSDisplay).grid(row=2, column=1)
        ScreePlotDisplay = BooleanVar()
        Checkbutton(frame2, text="Scree plot                               ", variable=ScreePlotDisplay).grid(row=3, column=1)

        self.CheckboxList=[CorrelationMDisplay.get(), UnrotatedFSDisplay.get(), ScreePlotDisplay.get()]

        frame3 = Frame(self.newwin)
        frame3.pack(side=TOP)
        Label(frame3, text="Faktori koji će biti ekstraktovani:").grid(row=0, column=0)

        def updateExtractionOption1(): #defining the extraction rule (eigenvalue>1)
            #self.FactorExtractionNumber=[ EigenValueCheck.get(), ConcreteValueCheck.get()]
            #print(self.FactorExtractionNumber)
            if EigenValueCheck.get():
                secondOption.deselect()
                self.FactorExtractionNumber = 1

        def updateExtractionOption2(): #defining the extraction rule (N first values)
            #self.FactorExtractionNumber=[ EigenValueCheck.get(), ConcreteValueCheck.get()]
            #print(self.FactorExtractionNumber)
            if ConcreteValueCheck.get():
                firstOption.deselect()
                self.FactorExtractionNumber = 1.34

        EigenValueCheck = BooleanVar()
        firstOption = Checkbutton(frame3, text="Gutman-Kaiser pravilo                           ",
                    variable=EigenValueCheck, command=updateExtractionOption1) #extract all the factors whose eigenvalue is greter than 1
        firstOption.grid(row=0, column=1)
        firstOption.select()
        ConcreteValueCheck = BooleanVar()
        secondOption = Checkbutton(frame3, text="Unos broja faktora koji će biti zadržani",
                    variable=ConcreteValueCheck, command=updateExtractionOption2)
        secondOption.grid(row=1, column=1)

        frame4 = Frame(self.newwin)
        frame4.pack(side=TOP)
        Label(frame4, text="Broj iteracija za konvergenciju:").grid(row=0, column=0)

        def callback(P): #making sure that the entry is a positive interger
            if str.isdigit(P) or P == "":
                return True
            else:
                return False

        vcmd = (frame4.register(callback))

        IterationNumber = Entry(frame4, validate='all', validatecommand=(vcmd, '%P'))
        IterationNumber.grid(row=0, column=1)
        self.IterationNumber = IterationNumber.get()

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



    def browse(self):
        """ Browses a .png file or all files and then puts it on the entry.
        """

        self.filepath.set(fd.askopenfilename(initialdir=self._initaldir,
                                             filetypes=self._filetypes))



if __name__ == '__main__':
    root = Tk()
    root.title("Aplikacija za faktorsku analizu podataka")
    labelfont = ('times', 10, 'bold')
    root.geometry("400x200")
    filetypes = (
        ('Comma-Separated Values', '*.csv'),
        ("All files", "*.*")
    )

    file_browser = ApplicationGUI(root, initialdir=r"C:\Users",
                          filetypes=filetypes)
    file_browser.pack(fill='y')
    root.mainloop()