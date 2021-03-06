from tkinter import *
from tkinter import filedialog as fd
import pandas as pd
import scipy as sp
import numpy as np
from factor_analyzer import *
import matplotlib.pyplot as plt
import copy


def Cronbach(N, Cov, Std):

    CovSum = 0
    if N < 2:
        return 1
    for i in range(N-1):
        CovSum += np.sum(Cov.iloc[i, i+1:])
    alpha = ((N**2)*(CovSum/float((N**2 - N)/2)))/float(np.sum(np.square(Std)) + CovSum*2)
    return alpha


def callback(P):  # making sure that the entry is a positive integer
    if str.isdigit(P) or P == "":
        return True
    else:
        return False


class FormattedPrint:

    def __init__(self, PObject, Text):
        self.PObject = PObject
        self.Text = Text
        self.Output = ''
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
        self._initialdir = initialdir
        self._create_widgets()
        self._display_widgets()
        self.newwin = NONE
        self.ListOfSelctedVariables = []  # selected variables for factor analysis
        self.Method = StringVar()  # PCA, MINRES, ML or PAF
        self.Method.set('minres')
        self.RotationMethod = None  # None, Varimax, Quartimax, Equamax, Promax or Oblimin
        self.RotationIterationNumber = StringVar()
        self.RotationIterationNumber.set(30)  # rotation iteration number
        self.df = pd.DataFrame  # Data frame
        self.printObject = FormattedPrint('_________________________'
                                          '_________________________'
                                          '_________________________',
                                          'Ispis aplikacije za faktorsku analizu')
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

        if self.newwin != NONE:
            self.newwin.destroy()
        self.newwin = Toplevel(root)
        self.newwin.resizable(width=False, height=False)
        self.newwin.title("Faktorska analiza: Odabir varijabli")
        self.newwin.geometry("500x300")

        frame1 = Frame(self.newwin, bg="white", width=180, height=200)
        frame1.place(x=40, y=30)
        label1 = Label(frame1, text="Postojeće varijable", bg="white", fg="black")
        label1.pack()
        scrollbar1 = Scrollbar(frame1)
        scrollbar1.pack(side=RIGHT, fill=Y)

        def SelectAll(i):
            if i == 1:
                listbox1.select_set(0, END)
                listbox1.event_generate("<<ListboxSelect>>")
            else:
                listbox2.select_set(0, END)
                listbox2.event_generate("<<ListboxSelect>>")

        listbox1 = Listbox(frame1, yscrollcommand=scrollbar1.set, selectmode=EXTENDED)
        for i in self.df.columns:
            listbox1.insert(END, str(i))
        listbox1.pack(side=LEFT, fill=BOTH)
        listbox1.bind("<Control-a>", lambda x: SelectAll(1))

        scrollbar1.config(command=listbox1.yview)

        frame2 = Frame(self.newwin, bg="white", width=180, height=200)
        frame2.place(x=280, y=30)
        label2 = Label(frame2, text="Odabrane varijable", bg="white", fg="black")
        label2.pack()
        scrollbar2 = Scrollbar(frame2)
        scrollbar2.pack(side=RIGHT, fill=Y)
        listbox2 = Listbox(frame2, yscrollcommand=scrollbar2.set)
        listbox2.pack(side=LEFT, fill=BOTH)
        listbox2.bind("<Control-a>", lambda x: SelectAll(2))
        scrollbar2.config(command=listbox2.yview)

        if self.ListOfSelctedVariables:
            for i in range(len(self.ListOfSelctedVariables)):
                listbox2.insert(END, (self.ListOfSelctedVariables[i]))

        frame3 = Frame(self.newwin, width=200, height=50)
        frame3.place(x=160, y=250)

        backButton = Button(frame3, text="  Nazad  ", bg="red", fg="white", command=self.newwin.destroy)
        backButton.pack(side=LEFT)

        nextButton = Button(frame3, text="Nastavi", bg="red", fg="white", command=self.ExtractionWindow)
        nextButton.pack(side=LEFT)

        frameMiddle = Frame(self.newwin, width=58, height=40)
        frameMiddle.place(x=225, y=120)

        def ForwardVariables():
            if listbox1.curselection():
                for i in listbox1.curselection():
                    if not (listbox1.get(i) in self.ListOfSelctedVariables):
                        listbox2.insert(END, str(listbox1.get(i)))
                        self.ListOfSelctedVariables.append(listbox1.get(i))

        def DeleteVariables():
            if listbox2.curselection():
                start = listbox2.curselection()[0]
                end = listbox2.curselection()[-1]
                for i in listbox2.curselection():
                    self.ListOfSelctedVariables.remove(listbox2.get(i))
                listbox2.delete(start, end)

        forwardButton = Button(frameMiddle, text=" > ", bg="red", fg="white", command=ForwardVariables)
        forwardButton.pack()
        deleteButton = Button(frameMiddle, text=" < ", bg="red", fg="white", command=DeleteVariables)
        deleteButton.pack()

        self.newwin.mainloop()

    def ExtractionWindow(self):

        if self.newwin != NONE:
            self.newwin.destroy()
        self.newwin = Toplevel(root)
        self.newwin.resizable(width=False, height=False)
        self.newwin.title("Faktorska analiza: Ekstrakcija")
        self.newwin.geometry("500x300")

        frame1 = Frame(self.newwin, width=500, height=300)
        frame1.pack(side=TOP)

        # Create a Tkinter variable
        tkvar = StringVar(self.newwin)

        # Dictionary with options
        choices = {'Principal Components Analysis', 'Minimum Residual',
                   'Maximum Likelihood'}
        tkvar.set('Minimum Residual')  # set the default option

        popupMenu = OptionMenu(frame1, tkvar, *choices)
        Label(frame1, text="Odaberi metodu:").pack(side=LEFT)
        popupMenu.pack(side=LEFT)

        # on change dropdown value
        def updateMethod(*args):
            tempMethod = tkvar.get()
            if tempMethod == 'Minimum Residual':
                self.Method.set('minres')

            elif tempMethod == 'Principal Components Analysis':
                self.Method.set('pca')

            elif tempMethod == 'Maximum Likelihood':
                self.Method.set('ml')

        # link function to change dropdown
        tkvar.trace('w', updateMethod)

        #Reinitialize Method
        if self.Method.get() == 'minres':
            tkvar.set('Minimum Residual')
            popupMenu = OptionMenu(frame1, tkvar, *choices)
        elif self.Method.get() == 'pca':
            tkvar.set('Principal Components Analysis')
            popupMenu = OptionMenu(frame1, tkvar, *choices)
        elif self.Method.get() == 'ml':
            tkvar.set('Maximum Likelihood')
            popupMenu = OptionMenu(frame1, tkvar, *choices)

        frame2 = Frame(self.newwin)
        frame2.place(relx=0.18, rely=0.2)
        Label(frame2, text="Prikaži sljedeće:").grid(row=1, column=0)

        def updateSelection():
            self.ShowCorrMatrix = CorrelationMDisplay.get()
            self.ShowUnrotatedFS = UnrotatedFSDisplay.get()
            self.ShowScreePlot = ScreePlotDisplay.get()

        CorrelationMDisplay = BooleanVar()
        Button1 = Checkbutton(frame2, text="Korelaciona matrica               ",
                              variable=CorrelationMDisplay, command=updateSelection)
        Button1.grid(row=1, column=1)
        UnrotatedFSDisplay = BooleanVar()
        Button2 = Checkbutton(frame2, text="Nerotirana faktorska rješenja",
                              variable=UnrotatedFSDisplay, command=updateSelection)
        Button2.grid(row=2, column=1)
        ScreePlotDisplay = BooleanVar()
        Button3 = Checkbutton(frame2, text="Scree plot                               ",
                              variable=ScreePlotDisplay, command=updateSelection)
        Button3.grid(row=3, column=1)
        #Reinitialize checkbox
        if self.ShowCorrMatrix == 1:
            Button1.select()
        if self.ShowUnrotatedFS == 1:
            Button2.select()
        if self.ShowScreePlot == 1:
            Button3.select()

        frame3 = Frame(self.newwin)
        frame3.place(relx=0.2, rely=0.5)
        Label(frame3, text="    Broj faktora:").grid(row=0, column=0)

        def updateExtractionOption(i): #defining the extraction rule (N first values)
            if i == 1:
                if self.GutmanKaiser.get():
                    secondOption.deselect()
                    self.NumberOfFactors.set(0)
                else:
                    secondOption.select()
            elif i == 2:
                if self.ManualInput.get():
                    firstOption.deselect()
                    self.GutmanKaiser.set(0)
                else:
                    firstOption.select()
                    self.GutmanKaiser.set(1)

        #EigenValueCheck = BooleanVar()
        firstOption = Checkbutton(frame3, text="Gutman-Kaiser pravilo                           ",
                    variable=self.GutmanKaiser, command=lambda: updateExtractionOption(1))
                    #extract all the factors whose eigenvalue is greter than 1
        firstOption.grid(row=0, column=1)

        #ConcreteValueCheck = BooleanVar()
        secondOption = Checkbutton(frame3, text="Unos broja faktora koji će biti zadržani",
                    variable=self.ManualInput, command=lambda: updateExtractionOption(2))
        secondOption.grid(row=1, column=1)

        vcmd = (frame3.register(callback))

        NumberOfFactors = Entry(frame3, validate='all', validatecommand=(vcmd, '%P'), textvariable=self.NumberOfFactors)
        NumberOfFactors.grid(row=2, column=1)

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
        self.newwin.resizable(width=False, height=False)
        self.newwin.title("Faktorska analiza: Rotacija")
        self.newwin.geometry("500x300")

        frame1 = Frame(self.newwin)
        frame1.pack(side=TOP)

        Label(frame1, text="Odaberi metodu rotacije:").pack(side=TOP)

        RotationMethod1Check = BooleanVar()
        firstOption = Checkbutton(frame1, text="None",
                    variable=RotationMethod1Check, command=lambda: updateRotationMethod(0))

        RotationMethod2Check = BooleanVar()
        secondOption = Checkbutton(frame1, text="Varimax",
                    variable=RotationMethod2Check, command=lambda: updateRotationMethod(1))

        RotationMethod3Check = BooleanVar()
        thirdOption = Checkbutton(frame1, text="Quartimax",
                    variable=RotationMethod3Check, command=lambda: updateRotationMethod(2))

        RotationMethod4Check = BooleanVar()
        fourthOption = Checkbutton(frame1, text="Equamax",
                    variable=RotationMethod4Check, command=lambda: updateRotationMethod(3))

        RotationMethod5Check = BooleanVar()
        fifthOption = Checkbutton(frame1, text="Promax",
                    variable=RotationMethod5Check, command=lambda: updateRotationMethod(4))

        RotationMethod6Check = BooleanVar()
        sixthOption = Checkbutton(frame1, text="Oblimin",
                    variable=RotationMethod6Check, command=lambda: updateRotationMethod(5))

        CBtnList = [firstOption, secondOption, thirdOption, fourthOption, fifthOption, sixthOption]
        RMList = [None, 'varimax', 'quartimax', 'equamax', 'promax', 'oblimin']

        def updateRotationMethod(index):

            for i in range(len(RMList)):
                if i != index:
                    CBtnList[i].deselect()

            self.RotationMethod = RMList[index]

        # Reinitialize checkbox
        CBtnList[RMList.index(self.RotationMethod)].select()

        firstOption.pack(side=TOP, anchor=W)
        secondOption.pack(side=TOP, anchor=W)
        thirdOption.pack(side=TOP, anchor=W)
        fourthOption.pack(side=TOP, anchor=W)
        fifthOption.pack(side=TOP, anchor=W)
        sixthOption.pack(side=TOP, anchor=W)

        frame2 = Frame(self.newwin)
        frame2.place(x=150, y=165)

        def updateSelection():
            self.ShowRotatedFS = RotatedMDisplay.get()

        RotatedMDisplay = BooleanVar()
        Button1 = Checkbutton(frame2, text="Prikaži rotirana rješenja",
                              variable=RotatedMDisplay, command=updateSelection)
        Button1.grid(row=1, column=1)

        # Reinitialize checkbox
        if self.ShowRotatedFS == 1:
            Button1.select()

        frame3 = Frame(self.newwin)
        frame3.place(x=80, y=200)
        Label(frame3, text="Broj iteracija za konvergenciju:").grid(row=0, column=0)

        vcmd2 = (frame3.register(callback))

        IterationNumber = Entry(frame3, validate='all', validatecommand=(vcmd2, '%P'),
                                 textvariable=self.RotationIterationNumber)
        IterationNumber.grid(row=0, column=1)

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
        frame1 = Frame(self.newwin, width=self.newwin.winfo_screenwidth()-300,
                       height=self.newwin.winfo_screenheight()-300)
        frame1.pack(fill=BOTH)
        label1 = Label(frame1, text="Rezultati", fg="black")
        label1.pack(fill=BOTH)
        scrollbar1 = Scrollbar(frame1)
        scrollbar1.pack(side=RIGHT, fill=Y)

        buffer = self.FactorProcessing()

        text = Text(frame1, width=self.newwin.winfo_screenwidth()-80, height=self.newwin.winfo_screenheight()-300)
        text.insert(END, buffer)
        text.config(state=DISABLED)
        text.pack()

        frame4 = Frame(self.newwin, width=0, height=5)
        frame4.place(relx=0.6, rely=0.9)
        frame5 = Frame(self.newwin, width=30, height=5)
        frame5.place(relx=0.67, rely=0.9)
        BackButton = Button(frame4, text="  Nazad ", bg="red", fg="white", command=self.RotationWindow)
        BackButton.pack()

        def SaveResults():
            file = open('Results.txt', 'w')
            file.write(text.get("1.0", END))
            file.close()
            if self.ShowScreePlot:
                plt.savefig('ScreePlot.png')

        SaveButton = Button(frame5, text="Sačuvaj", bg="red", fg="white", command=SaveResults)
        SaveButton.pack()

        frame6 = Frame(self.newwin, width=30, height=5)
        frame6.place(relx=0.9, rely=0.9)

        ExitButton = Button(frame6, text="   Izađi   ", bg="red", fg="white", command=self.newwin.destroy)
        ExitButton.pack(fill=BOTH)

        self.newwin.mainloop()

    def browse(self):
        self.filepath.set(fd.askopenfilename(initialdir=self._initialdir,
                                             filetypes=self._filetypes))

    def FactorProcessing(self):
        #Create a data frame of only selected variables
        SelectedDF = self.df[self.ListOfSelctedVariables]
        if SelectedDF.isnull().values.any():
            self.printObject.AppendPObject(np.sum(SelectedDF.isnull().values),'Broj podataka koji nedostaju:')
            self.printObject.AppendPObject('', 'Podaci koji nedostaju su popunjeni zaokruženom srednjom vrijednošću!')
            SelectedDF = SelectedDF.fillna(SelectedDF.mean().round(decimals=0))

        #Descriptive statistics
        dscStatsDF = pd.DataFrame({"Srednja vrijednost": SelectedDF.mean(axis=0),
                                   "Standardna dev.": SelectedDF.std(axis=0),
                                   "Kosost": SelectedDF.skew(axis=0),
                                   "Kurtoza": SelectedDF.kurtosis(axis=0)})

        #Testing the adequacy of the data frame
        #Bartlett's adequacy test
        chi_square_value, p_value = calculate_bartlett_sphericity(SelectedDF)
        if (p_value > 0.05):
            self.printObject.AppendPObject(p_value, 'Podaci nisu statistički '
                                                    'značajni ni adekvatni po Bartlett testu! p vrijednost:')
        else:
            self.printObject.AppendPObject(p_value, 'Podaci su statistički značajni'
                                                    ' i adekvatni po Bartlett testu! p vrijednost:')

        #Chi squared value
        self.printObject.AppendPObject(chi_square_value, 'Test nezavisnosti varijabli korelacione matrice \u03C7^2:')

        # Kaiser-Meyer-Olkin adequacy test
        kmo_per_item, kmo_total = calculate_kmo(SelectedDF)
        if (kmo_per_item[kmo_per_item < 0.5]).size != 0:
           self.printObject.AppendPObject(kmo_per_item, 'Podaci nisu adekvatni po Kaiser-Meyer-Olkin testu!')
        if (kmo_total < 0.6):
            self.printObject.AppendPObject(kmo_total, 'Podaci nisu adekvatni po Kaiser-Meyer-Olkin testu!')
        else:
            self.printObject.AppendPObject(kmo_total, 'Podaci su adekvatni po Kaiser-Meyer-Olkin testu!')

        #Get correlation matrix with Pearson method
        CorrMatrix = SelectedDF.corr(method="pearson")

        #Get Eigenvalues
        eigenvalues, eigenvectors = sp.linalg.eigh(CorrMatrix)
        evals_order = np.argsort(-eigenvalues)
        eigenvalues = eigenvalues[evals_order]
        eigenvectors = eigenvectors[:, evals_order]

        self.printObject.AppendPObject(self.Method.get(), 'Metoda ekstrakcije faktora:')

        #Kaiser-Gutman rule for number of factors
        if self.GutmanKaiser.get():
            # Get Kaiser-Gutman number of factors
            self.NumberOfFactors.set((eigenvalues > 1).sum())
            self.printObject.AppendPObject(self.NumberOfFactors.get(), 'Kaiser-Gutman broj faktora:')
        else:
            if int(self.NumberOfFactors.get()) > len(self.ListOfSelctedVariables):
                return ('Broj faktora ne smije biti veci od broja varijabli!')
            self.printObject.AppendPObject(self.NumberOfFactors.get(), 'Uneseni broj faktora:')

        self.printObject.AppendPObject(self.RotationMethod, 'Metoda rotacije:')
        self.printObject.AppendPObject(self.RotationIterationNumber.get(), 'Uneseni broj iteracija za rotaciju:')

        self.printObject.AppendPObject(dscStatsDF.to_string(), 'Deskriptivna statistika podataka:')

        method = self.Method.get()
        #making a dummy fa object with a valid method instead of pca
        if method == 'pca':
            method = 'ml'
        fa = FactorAnalyzer(impute='mean', is_corr_matrix=False,
                method=method, n_factors=int(self.NumberOfFactors.get()),
                            rotation=None, rotation_kwargs={}, use_smc=True)
        fa.fit(SelectedDF)
        columns = []
        for i in range(1, int(self.NumberOfFactors.get()) + 1):
            columns.append('Factor'+str(i))
        Loadings = pd.DataFrame(fa.loadings_, index=SelectedDF.columns,
                                columns=columns)
        if self.Method.get() == 'pca':
            #A - Loadings matrix
            #lambda - eigenvalues vector
            #U - eigenvector matrix
            # A[i,j] = sqrt(lambda[j])*U[i,j]
            temp = copy.deepcopy(eigenvectors)
            for i in range(len(eigenvalues)):
                temp[:, i] *= np.sqrt(eigenvalues[i])
            temp = temp[:, :int(self.NumberOfFactors.get())]
            Loadings = pd.DataFrame(temp, index=Loadings.index, columns=Loadings.columns)

        # If Show Scree Plot is selected
        if self.ShowScreePlot:
            # Create scree plot using matplotlib
            plt.plot(range(0, SelectedDF.shape[1]),
                     eigenvalues, marker='o')
            plt.plot(range(0, SelectedDF.shape[1]), np.ones(len(eigenvalues)), 'r--')
            plt.title('Scree Plot')
            plt.xlabel('Variables')
            plt.ylabel('Eigenvalues')
            plt.legend(('Eigenvalues', 'Eigenvalues = 1'))
            plt.grid()
            plt.show(block=False)

        # Calculate communalities for given loadings df
        communalities = (Loadings ** 2).sum(axis=1)
        communalities = (pd.DataFrame(communalities,
                                     columns=['Komunaliteti'])).\
                                     sort_values(by='Komunaliteti', ascending=False)

        RotatedM = copy.deepcopy(Loadings)

        if self.RotationMethod != None:
            # Create a rotator object
            rotator = Rotator(method=self.RotationMethod,
                              max_iter=int(self.RotationIterationNumber.get()))
            RotatedM = pd.DataFrame(rotator.fit_transform(Loadings), index=Loadings.index,
                                    columns=Loadings.columns)

            RotationSums = np.array((np.power(RotatedM.to_numpy(), 2)).sum(axis=0))
            Percentage3 = RotationSums * 100 / len(eigenvalues)
            CumulativeP3 = []

            for i in range(len(eigenvalues)):
                CumulativeP3.append(sum(Percentage3[:i + 1]))
                if i >= int(self.NumberOfFactors.get()):
                    RotationSums = np.append(RotationSums, 0)
                    Percentage3 = np.append(Percentage3, 0)

        ExtractionSums = np.array((np.power(Loadings.to_numpy(), 2)).sum(axis=0))

        Percentage1 = eigenvalues * 100 / len(eigenvalues)
        Percentage2 = ExtractionSums * 100 / len(eigenvalues)
        CumulativeP1 = []
        CumulativeP2 = []

        for i in range(len(eigenvalues)):
            CumulativeP1.append(sum(Percentage1[:i + 1]))
            CumulativeP2.append(sum(Percentage2[:i + 1]))
            if i >= int(self.NumberOfFactors.get()):
                ExtractionSums = np.append(ExtractionSums, 0)
                Percentage2 = np.append(Percentage2, 0)

        VarianceFrame = [eigenvalues, Percentage1, CumulativeP1, ExtractionSums, Percentage2, CumulativeP2,
                         ExtractionSums, Percentage2, CumulativeP2]

        if self.RotationMethod is not None:
            VarianceFrame = [eigenvalues, Percentage1, CumulativeP1, ExtractionSums, Percentage2, CumulativeP2,
                             RotationSums, Percentage3, CumulativeP3]

        ev = pd.DataFrame(np.transpose(VarianceFrame), columns=['Svojstvene vrijednosti:',
                                                                '% varijanse:', 'Kumulativni %:', 'Nakon ekstrakcije:',
                                                                '% varijanse:', 'Kumulativni %:', 'Nakon rotacije:',
                                                                '% varijanse:', 'Kumulativni %:'])

        self.printObject.AppendPObject(communalities.to_string(), '')
        self.printObject.AppendPObject(ev.to_string(), '')
        if self.ShowCorrMatrix:
            self.printObject.AppendPObject(CorrMatrix, "Korelaciona matrica:")
        if self.ShowUnrotatedFS:
            self.printObject.AppendPObject(Loadings.to_string(), "Ekstraktovani faktori bez rotacije:")

        #dropping variables with non-salient loadings
        if self.RotationMethod != None:
            lightRM = (RotatedM.where(np.abs(RotatedM.values) >= 0.45)).dropna(axis=0, how='all')
        else:
            lightRM = (Loadings.where(np.abs(Loadings.values) >= 0.45)).dropna(axis=0, how='all')
        # dropping variables with multiple salient loadings
        lightRM = lightRM[(lightRM.notnull().sum(axis=1) == 1)]

        if self.ShowRotatedFS:
            self.printObject.AppendPObject(RotatedM.to_string(), 'Rotirani faktori:')
            self.printObject.AppendPObject(lightRM.to_string(), 'Rotirani faktori > 0.45:')

        SortedVariables = pd.DataFrame(lightRM.abs().idxmax(axis=1).sort_values(axis=0),
                                       columns=['Faktori'])
        self.printObject.AppendPObject(SortedVariables.to_string(), 'Preslikavanje varijabli na faktore:')

        new_communalities = communalities.loc[SortedVariables.index, :]
        self.printObject.AppendPObject(new_communalities.to_string(), '')

        FinalLoadings = RotatedM.loc[SortedVariables.index, :]
        self.printObject.AppendPObject(FinalLoadings.to_string(), 'Final sorted loadings')

        CronbachAlphaDF = pd.DataFrame()
        for i in range(1, int(self.NumberOfFactors.get())+1):
            tempDF = SortedVariables.loc[SortedVariables['Faktori'] == ('Factor'+str(i))]
            VariableClusterDF = SelectedDF[tempDF.index.values]
            CovMatrix = VariableClusterDF.cov()
            StdMatrix = VariableClusterDF.std()
            CronbachAlphaDF = CronbachAlphaDF.append({'Factor': 'factor'+str(i),
            'Cronbachova alfa': Cronbach(len(VariableClusterDF.columns), CovMatrix, StdMatrix)}, ignore_index=True)

        self.printObject.AppendPObject(CronbachAlphaDF.to_string(), 'Mjera interne konzistentnosti varijabli:')

        return self.printObject.getOutput()


if __name__ == '__main__':

    root = Tk()
    root.title("Aplikacija za faktorsku analizu podataka")
    labelfont = ('times', 10, 'bold')
    root.geometry("500x200")
    root.resizable(width=False, height=False)
    AppObject = ApplicationGUI(root, initialdir=r"~/")
    AppObject.pack(fill='y')

    root.mainloop()
