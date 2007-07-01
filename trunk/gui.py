#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, string, types, fileinput
from Tkinter import *
from tkFont import *
from pyformat import *

# Gui Initialization
class MainFrame(Frame):
	def createWidgets(self, *options):
		# menu
		self.menu = Menu(self._master)
		self.menu_File = Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label='File', menu=self.menu_File,
				underline=0)
		self.menu_File.add_command(label='Exit', command=self.quit,
				underline=1, accelerator='Alt-X')
		self._master["menu"] = self.menu
		# hotkey
		def quit(event):
			self.quit()
		self.bind_all('<Alt-x>', quit)
		# textbox
		self.textbox_yscroll = Scrollbar(self._master, orient=VERTICAL)
		self.textbox = Text(self._master,
				yscrollcommand=self.textbox_yscroll.set,
				font=Font(family='Times New Roman', size=16))
		self.textbox_yscroll["command"] = self.textbox.yview
		self.textbox.pack(side=LEFT, expand=TRUE, fill=BOTH)
		self.textbox_yscroll.pack(side=RIGHT, fill=Y)
		self.textbox.bind('<KeyRelease>', self.textbox_keyrelease)
		self.textbox.focus_set()
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self._master = master
		self.pack()
		self.createWidgets()
		self.lastline = u''
		self.lastpos = ''
		self.lastchar = u''
		self.changed = False
	def textbox_keyrelease(self, event):
		#if event.keysym_num in range(32, 128):
		#	print "'"+event.keysym+"'",
		#else:
		#	print event.keysym_num,
		currentline = event.widget.get('insert linestart', 'insert lineend')
		currentpos = event.widget.index('insert - 1 chars')
		char = event.widget.get('insert - 1 chars')
		if event.keysym_num in range(32, 128) and char == event.char:
			if char in delimitrset:
				#i = len(currentline)-2
				#while i >= 0 and currentline[i] in delimitrset:
				#	i -= 1
				#while i >= 0 and not currentline[i] in delimitrset:
				#	i -= 1
				#if i < 0:
				#	i = 0
				#nowword = currentline[i:]
				#j = currentpos.index('.') + 1
				#nowwordpos = currentpos[:j] + `i`
				#print nowword, nowwordpos,
				#print '>', currentline, '=', 
				currentline = pyformat(currentline)
				#print currentline,
				event.widget.delete('insert linestart', 'insert lineend')
				event.widget.insert(currentpos, currentline)

if __name__ == '__main__':
	root = Tk()
	app = MainFrame(master = root)
	app.mainloop()
