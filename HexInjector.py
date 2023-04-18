from multiprocessing.connection import wait
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Frame, Button
from tkinter import messagebox
import sys
from flask import Flask, send_file
import tkinter.messagebox as messagebox

# This enables the user to scroll through the output display just using the touch pad up and down gestures (no need for a displayed line bar)
def move_cursor(event):
    if event.keysym == "Up":
        index = outputList.curselection()
        if index:
            index = int(index[0])
            if index > 0:
                outputList.selection_clear(index)
                outputList.selection_set(index - 1)
                outputList.activate(index - 1)
    elif event.keysym == "Down":
        index = outputList.curselection()
        if index:
            index = int(index[0])
            if index < outputList.size() - 1:
                outputList.selection_clear(index)
                outputList.selection_set(index + 1)
                outputList.activate(index + 1)


# This is just a functon that I though I will use but Stll potential to modify the code utilizin it\
# it add leading zeros to a given number
def add_leading_zeros(num, length):
    return str(num).zfill(length)


# An fast way to find the number of digits of a number
def countDigits(num):
    return len(str(num))


# Ends the program
def endSession():
    print("Have a great day")
    raise SystemExit


# Creates a unique name for each serial number
def getFileExtension():
    fileExtension = ""
    for c in Data:
        fileExtension += str(Data[c])
    return fileExtension


# Generate output for the generated new hex injected output
def generateoutput():
    z = 0
    checkVall = {}  # find if there is none correct memory addresses
    checkVall = {key: 0 for key in Data.keys()}  # Set all keys' value to 0
    outputList.delete(0, tk.END)
    file = open("hex" + getFileExtension(), "w")  # opens the file
    for index, binary in enumerate(pyhtnList):
        for x in Data:
            if ("04" == binary[6:8]) and (
                x == binary[2:6]
            ):  # checks for the 04 hex format
                if countDigits(Data[x]) == 4:
                    # Modify the hex numbers to the injected ones line to line
                    pyhtnList[index] = binary[:8] + Data[x] + binary[12:]
                    # Outputs changed hex numbers to the display console
                    outputList.insert(tk.END, f"{pyhtnList[index]}")
                    # records number of changes
                    z = z + 1
                    checkVall[
                        x
                    ] = 1  # says the values which have the been found whith addrresses
            elif ("00" == binary[6:8]) and (
                x == binary[2:6]
            ):  # checks for the 00 hex format
                # if hex = A2F then (10 * 16^2) + (2 * 16^1) + (15 * 16^0) = 2560 + 32 + 15 = 2575
                val = int(binary[0:2], 16) * 2
                if val == countDigits(Data[x]):
                    # Modify the hex numbers to the injected ones line to line
                    pyhtnList[index] = binary[:8] + Data[x] + binary[(val + 9) - 1 :]
                    # Outputs changed hex numbers to the display console
                    outputList.insert(tk.END, f"{pyhtnList[index]}")
                    z = z + 1
                    checkVall[
                        x
                    ] = 1  # says the values which have the been found whith addrresses
                else:
                    messagebox.showerror(
                        "Error",
                        f"Your serial number doesnt not match the number of required bits {val}",
                    )

        file.write(pyhtnList[index] + "\n")
    errorMessage = ""
    # There is no need for the if statement it will just make it NEGLIGIBLY faster (I liked the statement tbh so i kept it)
    if sum(value for value in checkVall.values() if isinstance(value, int)) != len(
        checkVall.keys()
    ):
        for key in checkVall:
            if checkVall[key] == 0:
                errorMessage += str(key) + " "
        messagebox.showerror("Error", f"{errorMessage} memory addresses was not found")
    Data.clear()
    checkVall.clear()
    file.close()
    # generatButton = tk.Button(frame, text="Download File", command=lambda: download(pyhtnList[index]))
    # generatButton.grid(row=3, column=2, padx=0)
    # generatButton1.grid(row=3, column=3, padx=0, pady=10)
    target_label_bg = tk.Label(
        frame, text="Number of Changes:" + str(z), font=("Arial", 8), width=20
    )
    target_label_bg.grid(row=1, column=2, pady=10)


Data = {}
listOfHistory = {}


def add_inputs():
    global Data
    global listOfHistory  # Used to check for similqr files outputs
    listd = []
    # Gets both serial and target addresses
    target_addresses = target_entry.get()
    serial_number = serial_entry.get()
    listd = target_addresses.split(" ")
    # Check if the file was outputed beforehand
    for key in listOfHistory:
        if key in target_addresses and listOfHistory[key] == serial_number:
            messagebox.showerror("Error", "The file have been already output before")
            return 0
    if target_addresses and serial_number:
        for i in listd:
            Data[i] = serial_number
            listOfHistory[i] = serial_number
        target_list.insert(
            tk.END,
            f"Target Addresses: {target_addresses} Serial Number: {serial_number}",
        )
        target_entry.delete(0, tk.END)
        serial_entry.delete(0, tk.END)
    else:
        messagebox.showerror(
            "Error", "Please enter both Target Addresses and Serial Number."
        )


# Deletes all the outputs in he GUI console
def clear_list():
    target_list.delete(0, tk.END)
    Data.clear()


# Closes a window
def exit_window():
    root.destroy()


# Open the hex file and organize it also check for some exceptions
def open_file():
    global file_path
    global pyhtnList
    file_path = filedialog.askopenfilename(
        defaultextension=".hex",
        filetypes=[
            ("Hex Files", "*.hex"),
            ("Text Files", "*.txt"),
            ("All Files", "*.*"),
        ],
    )
    if "file_path" in globals():
        try:
            with open(file_path, "rb") as hex_file:
                hex_file = hex_file.readlines()
                pyhtnList = []
                for line in hex_file:
                    line = line.decode("utf-8")
                    result = line.split(":", 1)
                    result1 = result[1].split("\r", 1)
                    pyhtnList.append(result1[0])
                messagebox.showinfo("File Path", "The file path used is: " + file_path)
        except FileNotFoundError:
            print(
                "The file specified could not be found. Please check the file path and try again."
            )
            sys.exit()
    else:
        print("No file selected")
    exit_window()


lets = 0
# All of under this is GUI implementation
root = tk.Tk()
root.title("File Input")
root.geometry("300x300")
root.eval("tk::PlaceWindow . center")

frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.1, anchor="n")

button = tk.Button(frame, text="Open File", command=open_file)
button.pack(side="right")

button1 = tk.Button(frame, text="Cancel", command=endSession)
button1.pack(side="left")

label1 = tk.Label(root, text="Welcome, Hex Injector!")
label1.pack(pady=100)

root.mainloop()

root = tk.Tk()
root.title("Input Window")
root.eval("tk::PlaceWindow . center")

frame = tk.Frame(root)
frame.pack(pady=30)

target_label = tk.Label(frame, text="Target Addresses:", bg="lightyellow", width=20)
target_label.grid(row=0, column=0, padx=5)

target_entry = tk.Entry(frame, width=40)
# target_entry.insert(0, "Multiple Addresses Ex: 0000 1100")
# target_entry.bind("<FocusIn>", lambda event: clear_entry(event, target_entry))
# target_entry.bind("<FocusOut>", lambda event: focusOut(event, target_entry))
target_entry.grid(row=0, column=1, padx=5)

serial_label = tk.Label(frame, text="Serial Number:", bg="lightyellow", width=20)
serial_label.grid(row=1, column=0, padx=5)

serial_entry = tk.Entry(frame, width=40)
serial_entry.grid(row=1, column=1, padx=5)

target_list = tk.Listbox(frame, width=70, height=20)
target_list.grid(row=2, column=0, columnspan=2, pady=10, sticky="s")

scrollbar = tk.Scrollbar(frame, orient="vertical")
scrollbar.grid(row=2, column=3, pady=10, sticky="ns")

outputList = tk.Listbox(frame, width=70, height=20, yscrollcommand=scrollbar.set)
outputList.grid(row=2, column=2, padx=20, pady=10, sticky="s")

scrollbar.config(command=outputList.yview, background="yellow", borderwidth=9)

add_button = tk.Button(frame, text="Add", command=add_inputs)
add_button.grid(row=3, column=0, pady=10)

clear_button = tk.Button(frame, text="Clear", command=clear_list)
clear_button.grid(row=3, column=1, pady=10)

generatButton = tk.Button(frame, text="Generate", command=generateoutput)
generatButton.grid(row=3, column=2, pady=10)

target_label_bg = tk.Label(
    frame, text=":Output Display:", font=("Arial", 10), bg="lightyellow", width=20
)
target_label_bg.grid(row=0, column=2, padx=5)

root.mainloop()
