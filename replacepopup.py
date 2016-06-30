#!/usr/bin/python

import tkinter
from addmovie_gui_util import center, clearApp
from addmovie_util import insert2DB

class ReplaceMoviePopUp:

	def replaceMovYes(self, event):
		""" User selects Yes to replace movie. Insert into db and close window

		"""
		# insert new entry in database
		insert2DB(self.moviePopUpGUI.movieDict)
		self.top.destroy()
		return("break")

	def replaceMovNo(self, event):
		""" User selects No to replace movie. Just close window

		"""
		self.top.destroy()
		return("break")

	def __init__(self, moviePopUpGUI, master):
		""" Initialize GUI to replace movie already in DB. 
			
			Parameters
			----------
			moviePopUpGUI : parent GUI class
			master : root Tk() instance

		"""
		tki = tkinter
		self.top = tki.Toplevel(master)
		self.moviePopUpGUI = moviePopUpGUI

		self.top.bind('<Control-q>', self.quit)
		# self.protocol("WM_DELETE_WINDOW", self.quit)

		# Warning text label to replace
		warningText = "\"{0}\" already in DB. Replace?"\
			.format(moviePopUpGUI.movieDict['title'])
		self.label1 = Label(self.top, text=warningText, height=0, width=50)
		self.label1.pack()
		
		# Yes Button
		self.yesButton = tkinter.Button(self.top, text="YES", width=20)
		self.yesButton.bind("<Return>", self.replaceMovYes)
		self.yesButton.pack(side='top',padx=0,pady=0)
		self.searchTextBox.bind("<Down>", self.focus_next_window)
		self.yesButton.focus_set()
		
		# No Button
		self.noButton = Button(self.top, text="NO", width=20)
		self.noButton.bind("<Return>", self.quit)
		self.searchTextBox.bind("<Up>", self.focus_next_window)
		self.noButton.pack(side='bottom',padx=0,pady=0)

		# Center message box on screen
		center(self.top)
        
	def quit(self, event):
		self.top.destroy()

	def focus_next_window(self, event):
		""" Change focus to next UI element

		"""
		event.widget.tk_focusNext().focus()
		return("break")