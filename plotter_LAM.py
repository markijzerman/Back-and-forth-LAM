#!/usr/bin/python3

# BACK AND FORTH FOR LAM BUDAPEST
# MARK IJZERMAN, 2024

# do this https://mac.install.guide/python/command-not-found-python if python install doesnt work

import pathlib
import os, sys

import serial
import time

import tkinter as tk
from tkinter import messagebox

import threading

class BackAndForthApp:
	def __init__(self, root):

			# init

		#  Print to note that plotter3 is started
		print('### Python launched now! ###')


		curPath = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0]
		global path_to_watch
		path_to_watch = curPath + '/grbl_out'
		print('Your folder path is',path_to_watch)

		ext = '.gcode'

		# Select only files with grbl extension
		self.grbl_files = [i for i in os.listdir(path_to_watch) if os.path.splitext(i)[1] == ext]
		print(self.grbl_files)

		self.root = root
		self.root.title("Back and Forth")

		self.is_running = False
		self.current_file_index = 0  # Track the current index of grbl_files

		# Set window size and background color
		self.root.geometry("400x500")
		#self.root.configure(bg="grey")

		# Title label
		self.title_label = tk.Label(root, text="BACK & FORTH", font=("Helvetica", 18, "bold"), fg="white")
		self.title_label.pack(pady=10)

		# Subtitle label
		self.subtitle_label = tk.Label(root, text="Sébastien Robert, LAM Budapest", font=("Helvetica", 14), fg="white")
		self.subtitle_label.pack(pady=5)

		# Software credit label
		self.software_label = tk.Label(root, text="Software 20240619 by Mark IJzerman", font=("Helvetica", 12, "italic"), fg="white")
		self.software_label.pack(pady=5)

		

		# Create buttons
		self.start_button = tk.Button(root, text="Start", command=self.start_function)
		self.start_button.pack(pady=10)

		self.pause_button = tk.Button(root, text="Pause", command=self.pause_function, state=tk.DISABLED)
		self.pause_button.pack(pady=10)

		self.home_button = tk.Button(root, text="Home", command=self.home_function)
		self.home_button.pack(pady=10)
		
		self.quit_button = tk.Button(root, text="Quit", command=self.quit_function)
		self.quit_button.pack(pady=10)

		# Create dropdown
		self.dropdown_var = tk.StringVar()
		self.dropdown_var.set(self.grbl_files[0])
		self.dropdown_menu = tk.OptionMenu(self.root, self.dropdown_var, *self.grbl_files)
		self.dropdown_var.trace("w", self.display_selected_option)
		self.dropdown_menu.pack(pady=10)

		# Create file label
		self.fileLabel = tk.Label(root, text="")
		self.fileLabel.pack(pady=10)
		self.fileLabel.config(text="[no file loaded]")

		# Create status label
		self.status = tk.Label(root, text="")
		self.status.pack(pady=10)
		self.status.config(text="Ready.")

		

		# Bind space bar key to toggle function
		self.root.bind('<space>', self.toggle_function)

		# Bind Escape key to quit function
		self.root.bind('<Escape>', lambda event: self.quit_function())


		# Open grbl serial port

		try:
			print('opening serial port')
			#s = serial.Serial('/dev/tty.usbserial-AR0JVJXA',115200)
			print('serial port is open')
		except:
			print('!!! WARNING !!! Serial NOT initialized!')
			messagebox.showwarning(title='Warning!', message='Serial device not found. Please plug in and restart application.')


	# Function to display the selected option
	def display_selected_option(self, *args):
		selected_option = self.dropdown_var.get()
		print(f"Selected option: {selected_option}")
		self.fileLabel.config(text=str("Selected: " + selected_option))
		self.current_file_index = self.grbl_files.index(selected_option)


	def start_function(self):
		self.is_running = True
		self.start_button.config(state=tk.DISABLED)
		self.pause_button.config(state=tk.NORMAL)
		
		# Start a new thread to run the function
		self.thread = threading.Thread(target=self.run_function, daemon=True)
		self.thread.start()
		self.status.config(text="Started.")

	def pause_function(self):
		self.is_running = False
		self.start_button.config(state=tk.NORMAL)
		self.pause_button.config(state=tk.DISABLED)
		print('paused')
		self.fileLabel.config(text="[no file loaded]")
		#f.close() # unneccesary?

	def home_function(self):
		self.is_running = False
		self.start_button.config(state=tk.NORMAL)
		self.pause_button.config(state=tk.DISABLED)
		self.status.config(text="homing...")
		time.sleep(1)
		#f.close()
		print('homing...')
		# Wake up grbl
		#s.write("\r\n\r\n".encode()) /// ENABLE
		#time.sleep(2)   # Wait for grbl to initialize 
		# s.flushInput()  # Flush startup text in serial input /// ENABLE
		print('GRBL is awake')
		#s.write(('%H' + '\n').encode()) # Send g-code block to grbl to home/// ENABLE
		# grbl_out = s.readline() # Wait for grbl response with carriage return ///ENABLE
		#print( ' : ' + (grbl_out.strip()).decode()) ///ENABLE
		self.status.config(text="Ready.")
		print('done homing...')



	def quit_function(self):
		self.status.config(text="Quitting...")
		self.is_running = False
		
		time.sleep(0.1)
		#s.close() /// ENABLE
		#if 'f' in globals():
		#	f.close()

		if hasattr(self, 'thread') and self.thread.is_alive():
			print('thread is running, quitting...')
			#self.thread.exit()
			sys.exit()

		
		print('QUIT NOW')
		self.root.withdraw()
		#self.root.quit()
		self.root.after(1, root.destroy())
		
		


	def toggle_function(self, event=None):
		print('space bar pressed')
		if self.is_running:
			self.pause_function()
		else:
			self.start_function()

	def run_function(self):
		try:
			while self.is_running:

				for idx in range(self.current_file_index, len(self.grbl_files)):
					if not self.is_running:
						break

					file = self.grbl_files[idx]
					print('Printing: ', file)
					self.status.config(text=str("Printing: " + file))
					self.fileLabel.config(text=str("file: " + file))

					# Update dropdown menu to show current file
					self.dropdown_var.set(file)

					# Wake up grbl
					#s.write("\r\n\r\n".encode()) /// ENABLE
					time.sleep(2)   # Wait for grbl to initialize 
					# s.flushInput()  # Flush startup text in serial input /// ENABLE
					print('GRBL is awake')
					self.status.config(text=str("GRBL is awake"))

					# Open g-code file
					with open(path_to_watch + '/' + file, 'r') as f:
						for line in f:
							if not self.is_running:
								break


							l = line.strip() # Strip all EOL characters for consistency
							print( 'Sending: ' + l)
							self.status.config(text=str("Sending: " + l))
							#s.write((l + '\n').encode()) # Send g-code block to grbl /// ENABLE
							# grbl_out = s.readline() # Wait for grbl response with carriage return ///ENABLE
							#print( ' : ' + (grbl_out.strip()).decode()) ///ENABLE
					
							# Simulate doing some work
							time.sleep(0.01) # remove this in final

					# Update current_file_index to resume from the next file after pause
					self.current_file_index = (idx + 1) % len(self.grbl_files)
			
			else:
				print('stopped the run function.')
				self.is_running = False

			self.status.config(text="Paused.")

		except Exception as e:
			print(f"An error occurred: {e}")
			# Handle the error gracefully, e.g., close resources and quit the program
			self.quit_function()

if __name__ == "__main__":
	root = tk.Tk()
	app = BackAndForthApp(root)
	root.mainloop()


