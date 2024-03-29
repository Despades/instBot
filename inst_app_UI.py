# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'bot_ui2.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1057, 676)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(30, 20, 991, 481))
        self.groupBox.setObjectName("groupBox")
        self.url_list = QtWidgets.QListWidget(self.groupBox)
        self.url_list.setGeometry(QtCore.QRect(440, 30, 521, 391))
        self.url_list.setObjectName("url_list")
        self.user_name = QtWidgets.QLabel(self.groupBox)
        self.user_name.setGeometry(QtCore.QRect(20, 220, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.user_name.setFont(font)
        self.user_name.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.user_name.setFrameShadow(QtWidgets.QFrame.Plain)
        self.user_name.setAlignment(QtCore.Qt.AlignCenter)
        self.user_name.setObjectName("user_name")
        self.photo = QtWidgets.QLabel(self.groupBox)
        self.photo.setEnabled(True)
        self.photo.setGeometry(QtCore.QRect(20, 30, 171, 171))
        self.photo.setText("")
        self.photo.setPixmap(QtGui.QPixmap("nonuser.jpg"))
        self.photo.setScaledContents(True)
        self.photo.setAlignment(QtCore.Qt.AlignCenter)
        self.photo.setObjectName("photo")
        self.inst_link = QtWidgets.QLineEdit(self.groupBox)
        self.inst_link.setGeometry(QtCore.QRect(20, 270, 401, 31))
        self.inst_link.setAlignment(QtCore.Qt.AlignCenter)
        self.inst_link.setObjectName("inst_link")
        self.progressBar = QtWidgets.QProgressBar(self.groupBox)
        self.progressBar.setGeometry(QtCore.QRect(20, 440, 401, 23))
        self.progressBar.setAutoFillBackground(False)
        self.progressBar.setStyleSheet("selection-background-color: rgb(245, 121, 0);\n"
"border-radius: 5px;\n"
"")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setObjectName("progressBar")
        self.groupBox_2 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_2.setGeometry(QtCore.QRect(130, 320, 291, 101))
        self.groupBox_2.setObjectName("groupBox_2")
        self.follow_check = QtWidgets.QRadioButton(self.groupBox_2)
        self.follow_check.setGeometry(QtCore.QRect(10, 30, 112, 23))
        self.follow_check.setObjectName("follow_check")
        self.download_check = QtWidgets.QRadioButton(self.groupBox_2)
        self.download_check.setGeometry(QtCore.QRect(130, 30, 141, 23))
        self.download_check.setObjectName("download_check")
        self.like_check = QtWidgets.QRadioButton(self.groupBox_2)
        self.like_check.setGeometry(QtCore.QRect(10, 60, 131, 23))
        self.like_check.setChecked(True)
        self.like_check.setObjectName("like_check")
        self.make_task = QtWidgets.QPushButton(self.groupBox_2)
        self.make_task.setGeometry(QtCore.QRect(160, 60, 101, 31))
        self.make_task.setObjectName("make_task")
        self.delete_unfollow_user = QtWidgets.QPushButton(self.groupBox)
        self.delete_unfollow_user.setGeometry(QtCore.QRect(210, 220, 211, 41))
        self.delete_unfollow_user.setObjectName("delete_unfollow_user")
        self.autorization_button = QtWidgets.QPushButton(self.groupBox)
        self.autorization_button.setGeometry(QtCore.QRect(210, 120, 101, 31))
        self.autorization_button.setObjectName("autorization_button")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_2.setGeometry(QtCore.QRect(210, 30, 161, 31))
        self.lineEdit_2.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_3.setGeometry(QtCore.QRect(210, 70, 161, 31))
        self.lineEdit_3.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.final_delete_users = QtWidgets.QPushButton(self.groupBox)
        self.final_delete_users.setGeometry(QtCore.QRect(780, 440, 181, 25))
        self.final_delete_users.setObjectName("final_delete_users")
        self.sistem_message_area = QtWidgets.QScrollArea(self.centralwidget)
        self.sistem_message_area.setGeometry(QtCore.QRect(30, 510, 991, 121))
        self.sistem_message_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.sistem_message_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sistem_message_area.setWidgetResizable(True)
        self.sistem_message_area.setObjectName("sistem_message_area")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 975, 119))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.sistem_message_area.setWidget(self.scrollAreaWidgetContents)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1057, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "Инстанграм бот"))
        self.user_name.setText(_translate("MainWindow", "Имя пользователя"))
        self.inst_link.setPlaceholderText(_translate("MainWindow", "введите ссылку пользователя или пост"))
        self.groupBox_2.setTitle(_translate("MainWindow", "действия с профилем"))
        self.follow_check.setText(_translate("MainWindow", "подписаться"))
        self.download_check.setText(_translate("MainWindow", "скачать контент"))
        self.like_check.setText(_translate("MainWindow", "поставить лайк"))
        self.make_task.setText(_translate("MainWindow", "Выполнить"))
        self.delete_unfollow_user.setText(_translate("MainWindow", "убрать неподписавшихся"))
        self.autorization_button.setText(_translate("MainWindow", "Авторизация"))
        self.lineEdit_2.setPlaceholderText(_translate("MainWindow", "Ваш логин"))
        self.lineEdit_3.setPlaceholderText(_translate("MainWindow", "Ваш пароль"))
        self.final_delete_users.setText(_translate("MainWindow", "Подтвердить удаление"))
