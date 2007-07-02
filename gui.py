#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: YIN Dian	version: 20070701
import sys, os, string, glob
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
		self.menu_Edit = Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label='Edit', menu=self.menu_Edit,
				underline=0)
		def changenowword():
			self.textbox.event_generate('<KeyPress-F5>')
		self.menu_Edit.add_command(label='Change current word', 
				command=changenowword, underline=0, 
				accelerator='F5')
		self.menu_Keyb = Menu(self.menu, tearoff=0)
		self.menu.add_cascade(label='Keyboard', menu=self.menu_Keyb,
				underline=0)
		self.generatekeyboardmenu(self.menu_Keyb, '*.rule')
		self._master["menu"] = self.menu
		self._master.title('Pinyin Keyboard')
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
		self.textbox.bind('<KeyPress-Return>', self.textbox_onreturn)
		self.textbox.bind('<KeyPress-F5>', self.textbox_donowword)
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
	def generatekeyboardmenu(self, menu, pattern):
		self.nowkbd = IntVar()
		self.nowkbd.set(0)
		i = 0
		pathprefix = '.'+os.sep+os.path.dirname(sys.argv[0])+os.sep
		filelist = glob.glob(pathprefix+pattern)
		filelist.sort()
		for fname in filelist:
			def selectrule(fname=fname, i=i):
				specifyrule(fname)
				print fname, 'selected'
				self.nowkbd.set(i)
			menu.add_radiobutton(label=`i`+'. '+fname, 
					command=selectrule, value=i,
					underline=0, variable=self.nowkbd)
			i += 1
		menu.invoke(0)
	def textbox_keyrelease(self, event):
		#if event.keysym_num in range(32, 128):
		#	print "'"+event.keysym+"'",
		#else:
		#	print event.keysym_num,
		currentline = event.widget.get('insert linestart', 'insert lineend')
		currentpos = event.widget.index('insert - 1 chars')
		#currentpos = event.widget.index('insert')
		char = event.widget.get('insert - 1 chars')
		if event.keysym_num in range(32, 128) and char == event.char:
			if char in delimitrset:
				j = currentpos.index('.') + 1
				i = k = int(currentpos[j:])
				while i >= 0 and currentline[i] in delimitrset:
					i -= 1
				while i >= 0 and not currentline[i] in delimitrset:
					i -= 1
				if i < 0:
					i = 0
				nowword = currentline[i:k]
				nowwordpos = currentpos[:j] + `i`
				print nowword.encode('gbk', 'replace'), nowwordpos,
				nowword = pyformat(nowword)
				print
				event.widget.delete(nowwordpos, currentpos)
				event.widget.insert(nowwordpos, nowword)
				##print '>', currentline, '=', 
				#currentline = pyformat(currentline)
				##print currentline,
				#event.widget.delete('insert linestart', 'insert lineend')
				#event.widget.insert('insert', currentline)
	def textbox_onreturn(self, event):
		currentline = event.widget.get('insert linestart', 'insert lineend')
		currentpos = event.widget.index('insert linestart')
		print currentline.encode('gbk', 'replace'), currentpos,
		currentline = pyformat(currentline)
		print
		event.widget.delete('insert linestart', 'insert lineend')
		event.widget.insert(currentpos, currentline)
	def textbox_donowword(self, event):
		currentline = event.widget.get('insert linestart', 'insert lineend')
		currentpos = event.widget.index('insert')
		j = currentpos.index('.') + 1
		i = k = int(currentpos[j:])
		if i == len(currentline):
			i -= 1
		while i >= 0 and currentline[i] in delimitrset:
			i -= 1
		while i >= 0 and not currentline[i] in delimitrset:
			i -= 1
		if i < 0:
			i = 0
		nowword = currentline[i:k]
		nowwordpos = currentpos[:j] + `i`
		print nowword.encode('gbk', 'replace'), nowwordpos,
		nowword = pyformat(nowword)
		print
		event.widget.delete(nowwordpos, currentpos)
		event.widget.insert(nowwordpos, nowword)

if __name__ == '__main__':
	root = Tk()
	app = MainFrame(master = root)
	app.mainloop()
