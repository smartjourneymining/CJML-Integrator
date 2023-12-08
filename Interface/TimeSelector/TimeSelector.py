
from tkinter import Label, Scrollbar,  Listbox, Button


class TimeSelector:
    def __init__(self, master, Touchpoint):
        self.fieldList = []
        self.master = master
        master.title("Mark timestamps")
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        master.rowconfigure(0, weight=1)
        yscrollbar = Scrollbar(master)
        yscrollbar.pack(side="right", fill="y")
        self.label = Label(master, text="Select fields containing Timestamps")
        self.label.pack()
        self.list = Listbox(master, selectmode="multiple", yscrollcommand=yscrollbar.set)

        self.list.pack(padx=10, pady=10, expand="ye", fill="both")

        for point in Touchpoint:
            self.list.insert(-1, point.name)
        self.button = Button(master, text="Continue", command=lambda:
                             self.convertSelectionsToList())
        self.button.pack()

    def convertSelectionsToList(self):
        for i in self.list.curselection():
            self.fieldList.append(self.list.get(i))
        self.master.destroy()
