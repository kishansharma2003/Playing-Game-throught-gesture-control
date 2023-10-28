import tkinter as tk
import subprocess

def launch_program():
    program_path = "C:\\Users\\Kishan Sharma\\Desktop\\bbracing.lnk"  # Replace with the path to your .lnk file
    subprocess.Popen(program_path, shell=True)


launch_program()

