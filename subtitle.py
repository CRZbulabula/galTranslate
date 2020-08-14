# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtWidgets, sip
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect
import qtawesome

from PIL import Image
from PIL import ImageChops

import sys, json, time, base64, threading, _thread, os

from setting import Setting
from screen import WScreenShot
from tencent import tencent

Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)


class Subtitle(QtWidgets.QMainWindow):

	def __init__(self):
		super().__init__()
		self._border = 5
		self._zoom_mod = False
		self._drag_mod = False
		self.setMouseTracking(True)
		self._init_ui()
		self._init_signal_and_slot()
		self._load_data()
	
	def _init_ui(self):
		self.resize(800, 200)
		self._main_widget = QtWidgets.QWidget()
		self._main_widget.setObjectName('_main_widget')
		self._main_layout = QtWidgets.QVBoxLayout()
		self._main_widget.setLayout(self._main_layout)

		# 创建上方部件
		self._up_widget = QtWidgets.QWidget()
		self._up_layout = QtWidgets.QHBoxLayout()
		self._up_widget.setLayout(self._up_layout)

		# 位于字幕君上方的功能按钮们
		self._button_settings = QtWidgets.QPushButton(qtawesome.icon('fa5s.cog', color='black'), "")
		self._button_cut = QtWidgets.QPushButton(qtawesome.icon('fa5s.cut', color='black'), "")
		self._button_play = QtWidgets.QPushButton(qtawesome.icon('fa5s.play', color='black'), "")
		self._button_pause = QtWidgets.QPushButton(qtawesome.icon('fa5s.pause', color='black'), "")
		self._button_mini = QtWidgets.QPushButton(qtawesome.icon('fa5s.minus', color='black'), "")
		self._button_close = QtWidgets.QPushButton(qtawesome.icon('fa5s.times', color='black'), "")

		# 利用QSS设定按钮三态
		self._up_widget.setStyleSheet('''
			QPushButton{border:none; border-radius:8px; background-color:rgb(14 , 150 , 254)}
			QPushButton:hover{background-color:rgb(44 , 137 , 255)}
			QPushButton:pressed{background-color:rgb(14 , 135 , 228); padding-left:3px; padding-top:3px}
		''')

		# 按钮层的自适应排版
		self._up_layout.addStretch(1)
		self._up_layout.addWidget(self._button_settings)
		self._up_layout.addStretch(1)
		self._up_layout.addWidget(self._button_cut)
		self._up_layout.addStretch(1)
		self._up_layout.addWidget(self._button_play)
		self._up_layout.addStretch(1)
		self._up_layout.addWidget(self._button_pause)
		self._up_layout.addStretch(1)
		self._up_layout.addWidget(self._button_mini)
		self._up_layout.addStretch(1)
		self._up_layout.addWidget(self._button_close)
		self._up_layout.addStretch(1)

		# 创建下方部件
		self._down_widget = QtWidgets.QWidget()
		self._down_layout = QtWidgets.QHBoxLayout()
		self._down_widget.setLayout(self._down_layout)

		# 这是字幕君~
		self._subtitle_label = QtWidgets.QLabel("これはテストテキストです")
		self._subtitle_label.setFont(QtGui.QFont("Roman times", 20, QtGui.QFont.Black))
		self._subtitle_label.adjustSize()
		
		self._down_layout.addStretch(1)
		self._down_layout.addWidget(self._subtitle_label)
		self._down_layout.addStretch(1)

		# 整体布局的自适应排版
		self._main_layout.addWidget(self._up_widget)
		self._main_layout.addStretch(1)
		self._main_layout.addWidget(self._down_widget)
		self._main_layout.addStretch(1)

		# 设置背景虚化、圆角边框、删除原始标签等美化操作
		self._main_widget.setStyleSheet('''QWidget#_main_widget{
			background:pink;
			border-top:1px solid white;
			border-bottom:1px solid white;
			border-left:1px solid white;
			border-top-left-radius:10px;
			border-bottom-left-radius:10px;
			border-top-right-radius:10px;
			border-bottom-right-radius:10px;
		}''')
		self.setWindowOpacity(0.9)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
		#self.setWindowFlags(Qt.WindowStaysOnTopHint)

		self.setCentralWidget(self._main_widget)
		self.centralWidget().setMouseTracking(True)

	def _init_signal_and_slot(self):
		self._button_close.clicked.connect(self.close)
		self._button_cut.clicked.connect(self._open_cutting)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+Alt+D")), self, self._open_cutting)
		self._button_play.clicked.connect(self._translating)
		self._button_pause.clicked.connect(self._stop)
		self._button_settings.clicked.connect(self._open_setting)

	def _load_data(self):
		filename = './config/config.json'
		with open(filename) as f:
			self._config_data = json.load(f)
			self._config_data = self._config_data[0]
		self._gap = self._config_data['gap']
		self._tencent_id = self._config_data['tId']
		self._tencent_Key = self._config_data['tKey']

	def _open_setting(self):
		self._setting = Setting()
		self._setting.show()

	def _open_cutting(self):
		self._cut = WScreenShot()
		self._cut._screen_signal.connect(self._save_points)
		self._cut.show()

	def _save_points(self, _start_point, _end_point):
		self._start_point = _start_point
		self._end_point = _end_point
		#print(self._start_point, self._end_point)
		screenshot = QtWidgets.QApplication.primaryScreen().grabWindow(QtWidgets.QApplication.desktop().winId())
		rect = QRect(self._start_point, self._end_point)
		outputRegion = screenshot.copy(rect)
		outputRegion.save('./img.png', format='PNG', quality=100)
		with open('./img.png', 'rb') as f:  # 以二进制读取图片
			data = f.read()
			encodestr = base64.b64encode(data) # 得到 byte 编码的数据
		result = tencent(encodestr, self._tencent_id, self._tencent_Key)
		# print(result)
		self._subtitle_label.setText(result)

	def _translate(self):
		_flag_first = True

		while self._playing == True:
			screenshot = QtWidgets.QApplication.primaryScreen().grabWindow(QtWidgets.QApplication.desktop().winId())
			rect = QRect(self._start_point, self._end_point)
			outputRegion = screenshot.copy(rect)
			outputRegion.save('./config/img_cur.png', format='PNG', quality=100)
			
			if _flag_first:
				outputRegion.save('./config/img_last.png', format='PNG', quality=100)
				with open('./config/img_last.png', 'rb') as f:  # 以二进制读取图片
					data = f.read()
					encodestr = base64.b64encode(data) # 得到 byte 编码的数据
				result = tencent(encodestr, self._tencent_id, self._tencent_Key)
				self._subtitle_label.setText(result)
				_flag_first = False
			else:
				_img_cur = Image.open('./config/img_cur.png')
				_img_last = Image.open('./config/img_last.png')
				diff = ImageChops.difference(_img_cur, _img_last)
				if diff.getbbox() is None:
					continue
				else:
					outputRegion.save('./config/img_last.png', format='PNG', quality=100)
					with open('./config/img_last.png', 'rb') as f:  # 以二进制读取图片
						data = f.read()
						encodestr = base64.b64encode(data) # 得到 byte 编码的数据
					result = tencent(encodestr, self._tencent_id, self._tencent_Key)
					self._subtitle_label.setText(result)
					_flag_first = False

	def _translating(self):
		self._playing = True
		_thread.start_new_thread(self._translate, ())

	def _stop(self):
		self._playing = False

	# 实现拖动窗口及窗口缩放事件
	def mousePressEvent(self, event):
		# 鼠标点击时记录起始位置
		if event.button() == Qt.LeftButton:
			self._mouse_pos = event.pos()

			# 判断拖动或缩放事件
			if self._mouse_pos.x() <= self._border:
				self._zoom_mod = True
			elif self.width() - self._mouse_pos.x() <= self._border:
				self._zoom_mod = True
			elif self._mouse_pos.y() <= self._border:
				self._zoom_mod = True
			elif self.height() - self._mouse_pos.y() <= self._border:
				self._zoom_mod = True
			else:
				self._drag_mod = True

			# 判断拖动方向
			if self._mouse_pos.x() <= self._border and self._mouse_pos.y() <= self._border:
				self._zoom_direction = LeftTop
			elif self.width() - self._border <= self._mouse_pos.x() and self.height() - self._border <= self._mouse_pos.y():
				self._zoom_direction = RightBottom
			elif self.width() - self._border <= self._mouse_pos.x() and self._mouse_pos.y() <= self._border:
				self._zoom_direction = RightTop
			elif self._mouse_pos.x() <= self._border and self.height() - self._border <= self._mouse_pos.y():
				self._zoom_direction = LeftBottom
			elif self._mouse_pos.x() <= self._border:
				self._zoom_direction = Left
			elif self.width() - self._border <= self._mouse_pos.x():
				self._zoom_direction = Right
			elif self._mouse_pos.y() <= self._border:
				self._zoom_direction = Top
			elif self.height() - self._border <= self._mouse_pos.y():
				self._zoom_direction = Bottom

		event.accept()

	def mouseMoveEvent(self, event):
		# 鼠标拖动时移动窗口
		if event.buttons() == Qt.LeftButton and self._mouse_pos and self._drag_mod == True:
			self.move(self.mapToGlobal(event.pos() - self._mouse_pos))
		
		# 鼠标移动时更新鼠标样式
		xPos = event.pos().x()
		yPos = event.pos().y()
		if xPos <= self._border and yPos <= self._border:
			self.setCursor(Qt.SizeFDiagCursor)
		elif self.width() - self._border <= xPos and self.height() - self._border <= yPos:
			self.setCursor(Qt.SizeFDiagCursor)
		elif self.width() - self._border <= xPos and yPos <= self._border:
			self.setCursor(Qt.SizeBDiagCursor)
		elif xPos <= self._border and self.height() - self._border <= yPos:
			self.setCursor(Qt.SizeBDiagCursor)
		elif xPos <= self._border:
			self.setCursor(Qt.SizeHorCursor)
		elif self.width() - self._border <= xPos:
			self.setCursor(Qt.SizeHorCursor)
		elif yPos <= self._border:
			self.setCursor(Qt.SizeVerCursor)
		elif self.height() - self._border <= yPos:
			self.setCursor(Qt.SizeVerCursor)
		else:
			self.setCursor(Qt.ArrowCursor)

		# 鼠标拖动时缩放窗口
		if event.buttons() == Qt.LeftButton and self._mouse_pos and self._zoom_mod == True:
			self._widget_resize(event)

		event.accept()

	def _widget_resize(self, event):
		xPos = event.pos().x()
		yPos = event.pos().y()
		x, y, w, h = self.x(), self.y(), self.width(), self.height()
		
		if self._zoom_direction == LeftTop:
			x += xPos
			w -= xPos
			y += yPos
			h -= yPos
		elif self._zoom_direction == RightBottom:
			w += xPos - self.width()
			h += yPos - self.height()
		elif self._zoom_direction == RightTop:
			y += yPos
			h -= yPos
			w += xPos - self.width()
		elif self._zoom_direction == LeftBottom:
			x += xPos
			w -= xPos
			h += yPos - self.height()
		elif self._zoom_direction == Left:
			x += xPos
			w -= xPos
		elif self._zoom_direction == Right:
			w += xPos - self.width()
		elif self._zoom_direction == Top:
			y += yPos
			h -= yPos
		elif self._zoom_direction == Bottom:
			h += yPos - self.height()
		self.setGeometry(x, y, w, h)

	def mouseReleaseEvent(self, event):
		# 鼠标松开结束事件
		self._mouse_pos = None
		self._drag_mod = False
		self._zoom_mod = False
		self.setCursor(Qt.ArrowCursor)
		event.accept()


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	gui = Subtitle()
	gui.show()
	sys.exit(app.exec_())
	os.system("pause")