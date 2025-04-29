import numpy as np
from tkinter import *
THEME_COLOR = "#375362"

root=Tk()
root.title("Interface")
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
label = Label(root, text="Μενού επιλογών")
label.grid(row=0,column=2000,pady=10,padx=10)
root.config(padx=20,pady=20,bg=THEME_COLOR)
root.geometry("1000x500+80+80")
def close_window():
    print("Τερματισμος")
    root.destroy()

buttons = []

# Ορισμός κοινής τιμής πλάτους (π.χ. 40 χαρακτήρες)
button_width = 50

buttons.append(Button(root, text="Μετρήσεις Θερμοκρασίας/υγρασίας", width=button_width))
buttons.append(Button(root, text="Μετρήσεις ρεύματος", width=button_width))
buttons.append(Button(root, text="Εκτιμήσεις παραμέτρων κινητήρα", width=button_width))
buttons.append(Button(root, text="Στατιστική ανάλυση ταξινόμησης", width=button_width))
buttons.append(Button(root, text="Επίδραση θορύβου στην μέτρηση ρεύματος κινητήρα", width=button_width))
buttons.append(Button(root, text="End programm", command=close_window, width=button_width))



for i in range(0,len(buttons)):
    buttons[i].grid(row=i+1, column=2000, padx=10, pady=10)

root.mainloop()

def close_window():
    print("Τερματισμος")
    root.destroy()