# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 15:02:03 2016

@author: dell1


This is a find and replace bot to stop having to do it by hand every time. 

It reads a file with the find in one column and the replace in the other 
"""

import csv, os
import fileinput
import tkinter as tk
from tkinter import filedialog


current_dir = os.getcwd()

print('Please select the find and replace key in the dialog box')

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(initialdir= current_dir)


    
with open(file_path, 'rt', ) as replace_key:
    reader = csv.reader(replace_key)
    
    for row in reader:
        
        if row[0] != '__ROOT__' and row[0] != '$PRE$':
            
            row[0] = ' ' + row[0] 
            row[1] = ' ' + row[1] 
            print(row)
                
        with fileinput.FileInput("visual-search.json", inplace=True) as file:    
            
            for line in file:
                print(line.replace(row[0], row[1]), end='')
                
replace_key.close()

with open(file_path, 'rt', ) as replace_key:
    reader = csv.reader(replace_key)

    for row in reader:

        if row[0] != '__ROOT__':

            row[0] = ' ' + row[0] 
            row[1] = ' ' + row[1]


        with fileinput.FileInput("configuration_fl.json", inplace=True) as file:    
			
            for line in file:
                print(line.replace(row[0], row[1]), end='')
                
replace_key.close()

print('find and replace complete.')
input("please press any key...")