import sys
import math
import os.path
import time
import re
import threading
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QGridLayout, QCheckBox)
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
		
		lblSpd = QLabel("Spd")
		grid.addWidget(lblSpd, 1, 2, 1, 1)
		self.txtSpeed = QLineEdit()
		self.txtSpeed.setText(str(self.speedDef))
		grid.addWidget(self.txtSpeed, 1, 3, 1, 1)
		
		self.cbLoop = QCheckBox()
		self.cbLoop.setText("Ping Pong")
		self.cbLoop.setChecked(True)
		grid.addWidget(self.cbLoop, 2, 0, 1, 2)

		lblFrm = QLabel("Frame")
		grid.addWidget(lblFrm, 2, 2, 1, 1)
		self.txtFrame = QLineEdit()
		self.txtFrame.setText("")
		grid.addWidget(self.txtFrame, 2, 3, 1, 1)
	
		btnStepBack = QPushButton("Step back")
		btnStepBack.clicked.connect(self.stepBackClicked)
		grid.addWidget(btnStepBack, 3, 0, 1, 2)
		btnStep = QPushButton("Step")
		btnStep.clicked.connect(self.stepClicked)
		grid.addWidget(btnStep, 3, 2, 1, 2)

		#btnStop = QPushButton("Stop")
		#btnStop.clicked.connect(self.stopClicked)
		#grid.addWidget(btnStop, 4, 0, 1, 2)
		self.btnPlay = QPushButton("Play")
		self.btnPlay.clicked.connect(self.playClicked)
		grid.addWidget(self.btnPlay, 4, 0, 1, 4)
		
		btnRefresh = QPushButton("Refresh frames")
		btnRefresh.clicked.connect(self.refreshClicked)
		grid.addWidget(btnRefresh, 5, 0, 1, 4)
	
		self.lbl = QLabel()
		grid.addWidget(self.lbl, 6, 0, 1, 4)
	
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
		else:
			self.stop()
		self.updateBtnPlay()
	
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
		self.endAnim()
	
	def endAnim(self):
		if self.txtFrame.text() != "":
			frame = -1
			try:
				frame = int(self.txtFrame.text())
			except ValueError:
				frame = -1
			if frame >= 0 and frame < len(self.frames):
				self.switchFrame(frame)
		
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

		self.switchFrame(newIdx)
	
	def switchFrame(self, newIdx):
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
	
	def updateBtnPlay(self):
		if self.playing:
			self.btnPlay.setText("Stop")
		else:
			self.btnPlay.setText("Play")

	def canvasChanged(self, canvas):
		pass
		
Application.addDockWidgetFactory(DockWidgetFactory("animlayers", DockWidgetFactoryBase.DockRight, AnimLayersDocker))
