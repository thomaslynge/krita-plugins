# AnimLayers version 1.1
# https://github.com/thomaslynge/krita-plugins
import sys
import math
import os.path
import time
import re
import threading
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QGridLayout, QCheckBox)
from krita import (Krita, Extension, DockWidget, DockWidgetFactory, DockWidgetFactoryBase)

animlayersinst = None

class layer:
	def __init__(self, node, visible):
		self.node = node
		self.visible = visible

def animlayersplay():
	global animlayersinst
	if animlayersinst != None:
		animlayersinst.playClicked()

def animlayersstepforth():
	global animlayersinst
	if animlayersinst != None:
		animlayersinst.stepClicked()

def animlayersstepback():
	global animlayersinst
	if animlayersinst != None:
		animlayersinst.stepBackClicked()

class AnimLayersExtension(Extension):
	def __init__(self, parent):
		super(AnimLayersExtension, self).__init__(parent)

	def setup(self):
		pass

	def createActions(self, window):
		actionplay = window.createAction("animlayers_play", i18n("Play"))
		actionplay.triggered.connect(animlayersplay)
		actionstepforth = window.createAction("animlayers_stepforth", i18n("Step forth"))
		actionstepforth.triggered.connect(animlayersstepforth)
		actionstepback = window.createAction("animlayers_stepback", i18n("Step back"))
		actionstepback.triggered.connect(animlayersstepback)

Scripter.addExtension(AnimLayersExtension(Krita.instance()))

class AnimLayersDocker(DockWidget):

	def __init__(self):
		super(AnimLayersDocker, self).__init__()

		self.speedDef = 500
		self.doc = None
		self.dir = 1
		self.frameIdx = -1
		self.frames = []
		self.layers = []
		self.layer = None
		self.playing = False
		self.outputlines = []
		self.outputlinescnt = []
		
		self.setWindowTitle(i18n("AnimLayers"))
		self.initUI()

		global animlayersinst
		animlayersinst = self		

	def initUI(self):
		widget = QWidget()
		widget.setContentsMargins(10, 10 , 10, 10)
		grid = QGridLayout()
		grid.setSpacing(10)
		
		row = 1
		lblKey = QLabel("Key")
		self.txtKey = QLineEdit()
		self.txtKey.setText("F")
		grid.addWidget(lblKey, row, 0)
		grid.addWidget(self.txtKey, row, 1)

		btnGetKey = QPushButton("Get key")
		btnGetKey.clicked.connect(self.getKeyClicked)
		grid.addWidget(btnGetKey, row, 2, 1, 2)
		
		row += 1
		btnStepBack = QPushButton("<")
		btnStepBack.clicked.connect(self.stepBackClicked)
		grid.addWidget(btnStepBack, row, 0, 1, 2)
		btnStep = QPushButton(">")
		btnStep.clicked.connect(self.stepClicked)
		grid.addWidget(btnStep, row, 2, 1, 2)
		
		row += 1
		self.btnPlay = QPushButton()
		self.btnPlay.clicked.connect(self.playClicked)
		self.updateBtnPlay()
		grid.addWidget(self.btnPlay, row, 0, 1, 4)
		
		row += 1
		self.cbLoop = QCheckBox()
		self.cbLoop.setText("Pong loop")
		self.cbLoop.setChecked(True)
		grid.addWidget(self.cbLoop, row, 0, 1, 2)

		lblSpd = QLabel("Speed")
		grid.addWidget(lblSpd, row, 2, 1, 1)
		self.txtSpeed = QLineEdit()
		self.txtSpeed.setText(str(self.speedDef))
		grid.addWidget(self.txtSpeed, row, 3, 1, 1)

		row += 1
		self.lbl = QLabel()
		grid.addWidget(self.lbl, row, 0, 1, 4)
	
		self.layout = grid
		widget.setLayout(grid)
		self.baseWidget = widget
		self.setWidget(widget)

	def getKeyClicked(self):
		doc = Application.activeDocument()
		if doc != None:
			name = doc.activeNode().name()
			parts = name.split(" ",1)
			self.txtKey.setText(parts[0])

	def playClicked(self):
		if self.playing == False:
			self.play()
		else:
			self.stop()
		self.updateBtnPlay()
	
	def play(self):
		self.playing = True
		self.buildFrames()
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
		
		idx = 0
		for layer in self.layers:
			layer.node.setVisible(layer.visible)
			if layer.visible:
				self.frameIdx = idx
			idx += 1
		if self.layer != None:
			doc = Application.activeDocument()
			if doc != None:
				doc.setActiveNode(self.layer)			
			
	def stepBackClicked(self):
		if self.frameIdx == -1:
			self.frameIdx = len(self.frames)
		self.step(-1)
		
	def stepClicked(self):
		self.step(1)

	def step(self, dir):
		if len(self.frames) == 0:
			self.buildFrames()

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
		prevFrame = self.frames[self.frameIdx]
		self.hideFrame(prevFrame)
		self.frameIdx = newIdx
		if self.playing == False:
			doc = Application.activeDocument()
			if doc != None:
				doc.setActiveNode(self.frames[self.frameIdx])
				idx = 0
				for frame in self.frames:
					if idx != newIdx and frame.visible():
						frame.setVisible(False)
					idx += 1		
		self.showFrame(self.frames[self.frameIdx])

	def buildFrames(self):
		self.frameIdx = -1
		self.frames = []
		self.layers = []
		doc = Application.activeDocument()
		if doc != None:
			nodes = doc.rootNode().childNodes()
			regexNode = r'^(' + re.escape(self.getKey()) + r'\s)(.*)'
			for node in nodes:
				if re.search(regexNode, node.name(), re.I):
					self.frames.insert(0,node)
					self.layers.insert(0, layer(node, node.visible()))
			self.layer = doc.activeNode()
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

	def updateBtnPlay(self):
		if self.playing:
			self.btnPlay.setText("Stop")
		else:
			self.btnPlay.setText("Play")

	def getKey(self):
		return self.txtKey.text().strip().lower()

	def clearOutput(self):
		self.outputlines = []
		self.outputlinescnt = []
		self.lbl.setText("")
	
	def output(self, text):
		if len(self.outputlines) > 0 and self.outputlines[0] == text:
			self.outputlinescnt[0] += 1
		else:		
			self.outputlines.insert(0, text)
			self.outputlinescnt.insert(0,1)
		
		lt = ""
		idx = 0
		for l in self.outputlines:
			if self.outputlinescnt[idx] > 1:
				lt += l + ' ('  + str(self.outputlinescnt[idx]) + ')\n'
			else:			
				lt += l + '\n'
			idx += 1
		self.lbl.setText(lt)

	def canvasChanged(self, canvas):
		pass

Application.addDockWidgetFactory(DockWidgetFactory("animlayers", DockWidgetFactoryBase.DockRight, AnimLayersDocker))
