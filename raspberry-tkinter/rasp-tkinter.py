import Tkinter
import tkMessageBox
import os,psutil
from subprocess import Popen
top = Tkinter.Tk()

def helloCallBack():
   os.system("node nodeapp/app.js &")

def helloshutdown():
   for process in psutil.process_iter():
    print(process.name())
    if process.name() == "node":
        print('Process found. Terminating it.')
        process.terminate()
        break
    else:
        print('Process not found: starting it.')
    
B = Tkinter.Button(top, text ="startdevice", command = helloCallBack)
B1 = Tkinter.Button(top, text ="Stopdevice", command = helloshutdown)
#B.place(relx=0.5, rely=0.5, anchor=Tkinter.CENTER)
#B1.place(relx=0.5, rely=0.5, anchor=Tkinter.CENTER)
B.pack(fill=Tkinter.X)
B1.pack(fill=Tkinter.X)
#B1.pack(fill=X)
w = 300 # width for the Tk root
h = 200 # height for the Tk root

# get screen width and height
ws = top.winfo_screenwidth() # width of the screen
hs = top.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# set the dimensions of the screen 
# and where it is placed
top.geometry('%dx%d+%d+%d' % (w, h, x, y))
top.mainloop()