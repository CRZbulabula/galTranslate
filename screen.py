# -*- coding: utf-8 -*-
# 转载自：http://blog.sina.com.cn/s/blog_71a803cb0102y53n.html

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

class WScreenShot(QWidget):
	
	_screen_signal = pyqtSignal(QPoint, QPoint)

	def __init__(self, parent=None):
		super(WScreenShot, self).__init__(parent)
		self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
		self.setStyleSheet('''background-color:black; ''')
		self.setWindowOpacity(0.6)
		desktopRect = QDesktopWidget().screenGeometry()
		self.setGeometry(desktopRect)
		self.setCursor(Qt.CrossCursor)
		self.blackMask = QBitmap(desktopRect.size())
		self.blackMask.fill(Qt.black)
		self.mask = self.blackMask.copy()
		self.isDrawing = False
		self.startPoint = QPoint()
		self.endPoint = QPoint()

	def _close(self):
		self._screen_signal.emit(self.startPoint, self.endPoint)
		self.close()

	def paintEvent(self, event):
		if self.isDrawing:
			self.mask = self.blackMask.copy()
			pp = QPainter(self.mask)
			pen = QPen()
			pen.setStyle(Qt.NoPen)
			pp.setPen(pen)
			brush = QBrush(Qt.white)
			pp.setBrush(brush)
			pp.drawRect(QRect(self.startPoint, self.endPoint))
			self.setMask(QBitmap(self.mask))
 
	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.startPoint = event.pos()
			self.endPoint = self.startPoint
			self.isDrawing = True
		elif event.button() == Qt.RightButton:
			self.close()
 
	def mouseMoveEvent(self, event):
		if self.isDrawing:
			self.endPoint = event.pos()
			self.update()
 
	def mouseReleaseEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.endPoint = event.pos()
			#screenshot = QApplication.primaryScreen().grabWindow(QApplication.desktop().winId())
			#rect = QRect(self.startPoint, self.endPoint)
			#outputRegion = screenshot.copy(rect)
			#outputRegion.save('./img.png', format='PNG', quality=100)
			self._close()
 
 
if __name__ == '__main__': 
	app = QApplication(sys.argv)
	win = WScreenShot()
	win.show()
	app.exec_()