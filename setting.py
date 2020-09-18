# -*- coding: utf-8 -*-

import json

from PyQt5 import  QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import sys
import qtawesome

Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)

class Setting(QtWidgets.QMainWindow):

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
		self.resize(600, 800)
		self._main_widget = QtWidgets.QWidget()
		self._main_layout = QtWidgets.QVBoxLayout()
		self._main_widget.setObjectName('_main_widget')
		self._main_widget.setLayout(self._main_layout)

		# 上方按钮
		self._up_widget = QtWidgets.QWidget()
		self._up_layout = QtWidgets.QHBoxLayout()
		self._up_widget.setLayout(self._up_layout)
		self._button_close = QtWidgets.QPushButton("")

		# 按钮三态
		self._up_widget.setStyleSheet('''
			QPushButton{border:none; border-radius:8px; background-color:rgb(14 , 150 , 254)}
			QPushButton:hover{background-color:rgb(44 , 137 , 255)}
			QPushButton:pressed{background-color:rgb(14 , 135 , 228); padding-left:3px; padding-top:3px}
		''')

		# 按钮行自适应排版
		self._up_layout.addStretch(1)
		self._up_layout.addWidget(self._button_close)

		# 创建tab页
		self._tabwidget = QtWidgets.QTabWidget()
		self._user_page = User()
		self._tabwidget.addTab(self._user_page, "账号信息")
		self._subtitle_page = subtitleCong()
		self._tabwidget.addTab(self._subtitle_page, "字幕设置")

		# 整体布局的自适应排版
		self._main_layout.addWidget(self._up_widget, 0, Qt.AlignTop)
		#self._main_layout.addStretch()
		self._main_layout.addWidget(self._tabwidget)
		
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
		self.setWindowFlags(Qt.FramelessWindowHint)

		self.setCentralWidget(self._main_widget)
		self.centralWidget().setMouseTracking(True)

	def _init_signal_and_slot(self):
		self._button_close.clicked.connect(self.close)

	def _load_data(self):
		filename = './config/config.json'
		with open(filename) as f:
			self._config_data = json.load(f)
			self._config_data = self._config_data[0]

		if 'ocrId' in self._config_data and self._config_data['ocrId'] != "":
			self._user_page._baiduocr_id.setText(self._config_data['ocrId'])
		else:
			self._user_page._baiduocr_id.setPlaceholderText("请输入")
			
		if 'ocrKey' in self._config_data and self._config_data['ocrKey'] != "":
			self._user_page._baiduocr_key.setText(self._config_data['ocrKey'])
		else:
			self._user_page._baiduocr_key.setPlaceholderText("请输入")
		
		if 'baiduId' in self._config_data and self._config_data['baiduId'] != "":
			self._user_page._baidu_id.setText(self._config_data['baiduId'])
		else:
			self._user_page._baidu_id.setPlaceholderText("请输入")
			
		if 'baiduKey' in self._config_data and self._config_data['baiduKey'] != "":
			self._user_page._baidu_Key.setText(self._config_data['baiduKey'])
		else:
			self._user_page._tencent_id.setPlaceholderText("请输入")

		if 'tId' in self._config_data and self._config_data['tId'] != "":
			self._user_page._tencent_id.setText(self._config_data['tId'])
		else:
			self._user_page._tencent_id.setPlaceholderText("请输入")

		if 'tKey' in self._config_data and self._config_data['tKey'] != "":
			self._user_page._tencent_Key.setText(self._config_data['tKey'])
		else:
			self._user_page._tencent_Key.setPlaceholderText("请输入")

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

class User(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		#self.setMouseTracking(True)
		self._init_ui()
		self._init_signal_and_slot()

	def _init_ui(self):
		self._main_layout = QtWidgets.QVBoxLayout()

		self._baiduocr_label = QtWidgets.QLabel("百度OCR")

		self._blayout_1 = QtWidgets.QHBoxLayout()
		self._bwidget_1 = QtWidgets.QWidget()
		self._bwidget_1.setLayout(self._blayout_1)
		self._ocrid_label = QtWidgets.QLabel("APIKey")
		self._baiduocr_id = QtWidgets.QLineEdit()
		self._blayout_1.addWidget(self._ocrid_label)
		self._blayout_1.addWidget(self._baiduocr_id)

		self._blayout_2 = QtWidgets.QHBoxLayout()
		self._bwidget_2 = QtWidgets.QWidget()
		self._bwidget_2.setLayout(self._blayout_2)
		self._bocrkey_label = QtWidgets.QLabel("SecretKey")
		self._baiduocr_key = QtWidgets.QLineEdit()
		self._blayout_2.addWidget(self._bocrkey_label)
		self._blayout_2.addWidget(self._baiduocr_key)

		self._baidu_label = QtWidgets.QLabel("百度翻译")

		self._blayout_3 = QtWidgets.QHBoxLayout()
		self._bwidget_3 = QtWidgets.QWidget()
		self._bwidget_3.setLayout(self._blayout_3)
		self._bid_label = QtWidgets.QLabel("APIKey")
		self._baidu_id = QtWidgets.QLineEdit()
		self._blayout_3.addWidget(self._bid_label)
		self._blayout_3.addWidget(self._baidu_id)

		self._blayout_4 = QtWidgets.QHBoxLayout()
		self._bwidget_4 = QtWidgets.QWidget()
		self._bwidget_4.setLayout(self._blayout_4)
		self._bkey_label = QtWidgets.QLabel("SecretKey")
		self._baidu_Key = QtWidgets.QLineEdit()
		self._blayout_4.addWidget(self._bkey_label)
		self._blayout_4.addWidget(self._baidu_Key)

		self._tencent_label = QtWidgets.QLabel("腾讯翻译")

		self._tlayout_1 = QtWidgets.QHBoxLayout()
		self._twidget_1 = QtWidgets.QWidget()
		self._twidget_1.setLayout(self._tlayout_1)
		self._tid_label = QtWidgets.QLabel("SecretId")
		self._tencent_id = QtWidgets.QLineEdit()
		self._tlayout_1.addWidget(self._tid_label)
		self._tlayout_1.addWidget(self._tencent_id)

		self._tlayout_2 = QtWidgets.QHBoxLayout()
		self._twidget_2 = QtWidgets.QWidget()
		self._twidget_2.setLayout(self._tlayout_2)
		self._tkey_label = QtWidgets.QLabel("SecretKey")
		self._tencent_Key = QtWidgets.QLineEdit()
		self._tlayout_2.addWidget(self._tkey_label)
		self._tlayout_2.addWidget(self._tencent_Key)

		self._button_save = QtWidgets.QPushButton("保存")
		self._buttom_widget = QtWidgets.QWidget()
		self._buttom_layout = QtWidgets.QHBoxLayout()
		self._buttom_widget.setLayout(self._buttom_layout)
		self._buttom_layout.addStretch(1)
		self._buttom_layout.addWidget(self._button_save)
		self._buttom_layout.addStretch(1)

		self._main_layout.addWidget(self._baiduocr_label)
		self._main_layout.addWidget(self._bwidget_1)
		self._main_layout.addWidget(self._bwidget_2)
		self._main_layout.addWidget(self._baidu_label)
		self._main_layout.addWidget(self._bwidget_3)
		self._main_layout.addWidget(self._bwidget_4)
		self._main_layout.addWidget(self._tencent_label)
		self._main_layout.addWidget(self._twidget_1)
		self._main_layout.addWidget(self._twidget_2)
		self._main_layout.addWidget(self._buttom_widget)
		self.setLayout(self._main_layout)

	def _init_signal_and_slot(self):
		self._button_save.clicked.connect(self._save)

	def _save(self):
		result = []
		filename = './config/config.json'

		with open(filename) as f:
			self._config_data = json.load(f)
			self._config_data = self._config_data[0]
		
		self._config_data['ocrId'] = self._baiduocr_id.text()
		self._config_data['ocrKey'] = self._baiduocr_key.text()
		self._config_data['baiduId'] = self._baidu_id.text()
		self._config_data['baiduKey'] = self._baidu_Key.text()
		self._config_data['tId'] = self._tencent_id.text()
		self._config_data['tKey'] = self._tencent_Key.text()
		result.append(self._config_data)

		with open(filename, 'w') as f:
			json.dump(result, f, indent = 4)

class subtitleCong(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		#self.setMouseTracking(True)
		self._init_ui()
		#self._init_signal_and_slot()

	def _init_ui(self):
		self._main_layout = QtWidgets.QVBoxLayout()

		self._tencent_label = QtWidgets.QLabel("截屏快捷键：Ctrl + Alt + D")
		self._main_layout.addWidget(self._tencent_label)

		self.setLayout(self._main_layout)

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	gui = Setting()
	gui.show()
	sys.exit(app.exec_())