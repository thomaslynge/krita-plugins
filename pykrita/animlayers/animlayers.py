import sys
import math
import os.path
import time
import re
import threading
from PyQt5.QtWidgets import (QWidget, QLabel, QMessageBox, QPushButton, QToolTip, QHBoxLayout, QVBoxLayout, QListView, QLineEdit, QTextEdit, QGridLayout, QCheckBox)
from PyQt5.QtGui import QFont
from krita import (Krita, Extension, DockWidget, DockWidgetFactory, DockWidgetFactoryBase)

class AnimLayersDocker(DockWidget):

	def __init__(self):
		super(AnimLayersDocker, self).__init__()

		self.speedDef = 500
		self.doc = None
		self.dir = 1
		self.frameIdx = -1
		self.frames = []
		self.key = ""
		self.playing = False
		
		self.setWindowTitle("Anim Layers")
		self.initUI()

	def initUI(self):
		widget = QWidget()
		widget.setContentsMargins(10, 10 , 10, 10)
		grid = QGridLayout()
		grid.setSpacing(10)
				
		lblKey = QLabel("Key")
		self.txtKey = QLineEdit()
		self.txtKey.setText("F")
		grid.addWidget(lblKey, 1, 0)
		grid.addWidget(self.txtKey, 1, 1)
		
		self.txtSpeed = QLineEdit()
		self.txtSpeed.setText(str(self.speedDef))
		grid.addWidget(self.txtSpeed, 1, 2, 1, 2)
		
		self.cbLoop = QCheckBox()
		self.cbLoop.setText("Loop")
		self.cbLoop.setChecked(True)
		grid.addWidget(self.cbLoop, 2, 0, 1, 2)
		
		btnStepBack = QPushButton("Step back")
		btnStepBack.clicked.connect(self.stepBackClicked)
		grid.addWidget(btnStepBack, 3, 0, 1, 2)
		btnStep = QPushButton("Step")
		btnStep.clicked.connect(self.stepClicked)
		grid.addWidget(btnStep, 3, 2, 1, 2)

		btnStop = QPushButton("Stop")
		btnStop.clicked.connect(self.stopClicked)
		grid.addWidget(btnStop, 4, 0, 1, 2)
		btnPlay = QPushButton("Play")
		btnPlay.clicked.connect(self.playClicked)
		grid.addWidget(btnPlay, 4, 2, 1, 2)
		
		self.lbl = QLabel()
		grid.addWidget(self.lbl, 5, 0, 1, 2)

		btnRefresh = QPushButton("Refresh")
		btnRefresh.clicked.connect(self.refreshClicked)
		grid.addWidget(btnRefresh, 6, 0, 1, 2)
	
		self.layout = grid
		widget.setLayout(grid)
		self.baseWidget = widget
		self.setWidget(widget)
	
	def refreshClicked(self):
		self.dir = 1
		self.refresh(True)
	
	def getKey(self):
		return self.txtKey.text().strip().lower()

	def playClicked(self):
		if self.playing == False:
			self.play()

	def stopClicked(self):
		self.stop()
	
	def play(self):
		self.playing = True
		self.stop_event=threading.Event()
		self.c_thread=threading.Thread(target=self.playEvent, args=(self.stop_event,))
		self.c_thread.start()
	
	def stop(self):
		self.stop_event.set()
		self.playing = False
	
	def playEvent(self,stop_event):
		state=True
		while state and not stop_event.isSet():	
			speed = self.speedDef
			if self.txtSpeed.text() != "":
				try:
					speed = int(self.txtSpeed.text())
				except ValueError:
					speed = self.speedDef
			time.sleep(speed / 1000)
			self.step(1)	
	
	def stepBackClicked(self):
		if self.frameIdx == -1:
			self.frameIdx = len(self.frames)
		self.step(-1)
		
	def stepClicked(self):
		self.step(1)
	
	def step(self, dir):
		self.refresh(False)
		if self.doc == None:
			return

		lastIdx = len(self.frames) - 1
		if lastIdx < 0:
			return
		
		loop = self.cbLoop.isChecked()
		if loop == False:
			self.dir = 1
		
		newIdx = self.frameIdx + self.dir * dir
		
		if newIdx > lastIdx:
			if loop:
				self.dir = -1 * dir
				newIdx = max(0,lastIdx - 1)
			else:
				newIdx = 0
		elif newIdx < 0:
			if loop:
				self.dir = 1 * dir
				newIdx = min(lastIdx,1)
			else:
				newIdx = lastIdx
			
		self.hideFrame(self.frames[self.frameIdx])
		self.frameIdx = newIdx
		self.showFrame(self.frames[self.frameIdx])	
		
	def refresh(self, forceBuild):
		self.clearOutput()
		doc = Application.activeDocument()
		requestBuild = forceBuild
		
		if self.key != self.getKey():
			self.key = self.getKey()
			requestBuild = True
		
		if doc == None:
			self.doc = None
			return		
		if doc != self.doc:
			self.doc = doc
			self.dir = 1
			requestBuild = True
			
		if requestBuild == True:
			self.buildFrames(doc)
		
	def buildFrames(self, doc):
		self.frameIdx = -1
		self.frames = []
		nodes = doc.rootNode().childNodes()
		regexNode = r'^(' + re.escape(self.key) + r'\s)(.*)'
		self.output("Regex: " + regexNode)
		for node in nodes:
			if re.search(regexNode, node.name(), re.I):
				self.frames.insert(0,node)
		
		if len(self.frames)==0:
			return

		idx = 0	
		for frame in self.frames:
			if self.frameIdx == -1 and frame.visible():
				self.frameIdx = idx
				self.showFrame(frame)
			else:
				self.hideFrame(frame)
			idx = idx + 1
		
	def showFrame(self, frame):
		frame.setVisible(True)
		frame.rotateNode(math.degrees(0))		

	def hideFrame(self, frame):
		frame.setVisible(False)
		
	def clearOutput(self):
		self.lbl.setText("");
	
	def output(self, text):
		curr = self.lbl.text()
		self.lbl.setText(curr + text + '\n')
		#reply = QMessageBox.question(self, 'Message',
		#	text, QMessageBox.Yes | 
		#	QMessageBox.No, QMessageBox.No)
	
	def canvasChanged(self, canvas):
		"""
		Override canvasChanged from :class:`DockWidget`.
		This gets called when the canvas changes.
		You can also access the active canvas via :func:`DockWidget.canvas`
		Parameter `canvas` can be null if the last document is closed
		"""
		#self._label.setText("AnimLayersDocker: canvas changed")		
				
Application.addDockWidgetFactory(DockWidgetFactory("animlayers", DockWidgetFactoryBase.DockRight, AnimLayersDocker))
