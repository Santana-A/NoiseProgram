from usb.core import find as finddev
import subprocess
import os
import numpy as np
import sys
import tkinter as tk
from tkinter import *

#create root
root = tk.Tk()
root.title('Noise Program')
root.geometry('400x400')
root.resizable(0,0)

#function that runs hackrf_sweep
def sweep():
	#capture output of hackrf_sweep and put it in stdout.txt
	with open("stdout.txt","wb") as out, open("stderr.txt","wb") as err:
		process = subprocess.Popen(['hackrf_sweep', '-1'], stdout=out,stderr=err)
		try:
		    print('Running process', process.pid)
		    process.wait(timeout=2)
		except subprocess.TimeoutExpired:
		    print('Timed out - killing', process.pid)
		    process.kill()
		print("Done")


	dev = finddev(idVendor=0x1d50, idProduct=0x6089)
	dev.reset()

	#transfer contents of out.txt into 2D array
	d = '/home/santana/auto'

	array2D = []

	#rows = len(array2D)
	
	for filename in os.listdir(d):
	    if not filename.endswith('.txt'):
	    	continue

	    with open('stdout.txt', 'r') as f:
	    	for line in f.readlines():
	    		array2D.append(line.split(','))
	    		
	#delete irrelevant info columns
	array2D = np.delete(array2D,0,1)
	array2D = np.delete(array2D,0,1)

	#delete duplicate frequency data
	arrSlice = array2D[:,[0,1,2,3]]
	_, unq_row_indices = np.unique(arrSlice,return_index=True,axis=0)
	unique = array2D[unq_row_indices]

	#find strongest signals in each row of the data
	u_slice = unique[:,[4,5,6,7,8]]
	arr = np.array(u_slice).astype(np.float)
	#print(arr.max(axis=1))
	arrMax = arr.max(axis=1)
	
	f_slice = unique[:,[0]]
	freq_arr = np.array(f_slice).flatten()
	#print(freq_arr[0])
	
	arr2 = np.array(unique).astype(np.float)

	row = len(arrMax)
	
	arrMaxs = np.sort(arrMax)[::-1]
	strongSignal = []
	
	for i in range(0, 40):
		#print(arrMaxs[i])
		r, c = (np.where(arr2 == arrMaxs[i]))
		row_num = int(r[0])
		col_num = int(c[0])
		sfreq = freq_arr[row_num]
		if int(col_num) == 4:
			strfreq = int(sfreq) 
		elif int(col_num) == 5:
			strfreq = int(sfreq) + 2000000
		elif int(col_num) == 6:
			strfreq = int(sfreq) + 3000000
		elif int(col_num) == 7:
			strfreq = int(sfreq) + 4000000
		elif int(col_num) == 8:
			strfreq = int(sfreq) + 5000000
		strongSignal.append(int(strfreq))
		
	
	v = tk.StringVar(root, "1")
	
	vscrollbar = tk.Scrollbar(root)
	c= tk.Canvas(root,width=400,height=100,scrollregion=(0,0,200,300),yscrollcommand=vscrollbar.set)
	vscrollbar.config(command=c.yview)
	vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
	f=tk.Frame(c) #Create the frame which will hold the widgets
	c.pack(side="left", fill="both")

	#Updated the window creation
	c.create_window(0,0,window=f, anchor='nw')
	
	rows = len(strongSignal)
	values = []
	# Dictionary to create multiple buttons
	for i in range(0,40):
		if strongSignal[i] > 0:
			values.append((str(strongSignal[i]) + " Hz", int(strongSignal[i])))
	
	#remove duplicates
	signals = []
	for x in values:
    		if x not in signals:
    			signals.append(x)
	
	# Loop is used to create multiple Radiobuttons
	# rather than creating each button separately
	for text, value in signals:
		tk.Radiobutton(f, text = text, variable = v, value = value, command= lambda: selected(v)).pack(anchor=W, fill=tk.Y)
		
	root.update()
	c.config(scrollregion=c.bbox("all"))
def selected(v):
	for widget in buttons.winfo_children():
		widget.destroy()
		
	selectedButton = v.get()
	noisy = tk.Button(buttons, text="Run Interference", width=48, command= lambda: interference(selectedButton))
	noisy.pack(side=BOTTOM)
	
	
	
def interference(sig):
	process2 = subprocess.Popen(['hackrf_transfer', '-t', 'noise', '-f', str(sig), '-s', '100000', '-l', '16', '-g', '0', '-x', '47'])
	try:
		print('Running process2', process2.pid)
		process2.wait(timeout=7)
	except subprocess.TimeoutExpired:
		print('Timed out - killing', process2.pid)
		process2.kill()
	print("Done")
	

	
	
def customEntry():
	for widget in buttons.winfo_children():
		widget.destroy()
	
	canvas = tk.Canvas(root, height=400, width=400)
	canvas.pack()
	
	label = tk.Label(root, text='Enter Frequency')
	label.config(font=('helvetica', 10))
	canvas.create_window(200, 100, window=label)

	freq = tk.Entry(root) 
	canvas.create_window(200, 140, window=freq)
	
	noisy = tk.Button(buttons, text="Run Interference", width=48, command= lambda: customSelect(freq))
	noisy.pack()
	

	#freq = tk.Entry (root) 
	#canvas1.create_window(200, 140, window=freq)
	
	#label = tk.Label(root, text='Enter Frequency')
	#label.config(font=('helvetica', 10))
	#canvas1.create_window(200, 100, window=label)
	
	#noisy = tk.Button(buttons, text="Run Interference", width=48, command= lambda: customSelect(freq))
	#noisy.pack()
	
	
	
	
def customSelect(v):
	for widget in buttons.winfo_children():
		widget.destroy()
		
	selectedButton = v.get()
	noisy = tk.Button(buttons, text="Run Interference", width=48, command= lambda: customInterference(selectedButton))
	noisy.pack()
	
def customInterference(frequency):	
	process2 = subprocess.Popen(['hackrf_transfer', '-t', 'noise', '-f', str(frequency), '-s', '100000', '-l', '16', '-g', '0', '-x', '47'])
	try:
		print('Running process2', process2.pid)
		process2.wait(timeout=7)
	except subprocess.TimeoutExpired:
		print('Timed out - killing', process2.pid)
		process2.kill()
	print("Done")
	
	
	

#create buttons
buttons = tk.Frame(root)
buttons.pack(side='bottom', fill='x')

start = tk.Button(buttons, text="Start Sweep", width=48, command=sweep)
start.pack()

custom = tk.Button(buttons, text="Custom Frequency", width=48, command=customEntry)
custom.pack()

#custom = tk.Button(root, text="Custom Frequency", width=48, command=customEntry)
#custom.pack(side=BOTTOM)

#start = tk.Button(root, text="Start Sweep", width=48, command=sweep)
#start.pack(side=BOTTOM)


root.mainloop()
