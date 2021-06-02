import sys
import requests
import datetime
import time
import random
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QThread
import json
import os
from inst_app_UI import Ui_MainWindow
from connect_module import SeleniumWorkerLogin, SeleniumWorkerTask
from auth_data import username, password




class InstDespadesBot(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        QtWidgets.QTabWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.chrome_opt = webdriver.ChromeOptions()
        self.chrome_opt.add_argument('--disable-gpu')#если не запускается и выдает ошибки, связанные с gpu
        self.browser = webdriver.Chrome('./drivers/chromedriver', chrome_options = self.chrome_opt)

        self.message_layout = QtWidgets.QVBoxLayout()#непосредственный контейнер для системных сообщений, в него складываем QLabel
        self.widget_messages = QtWidgets.QWidget()#контейнер для message_container, так как напрямую message_layout нельзя ложить в self.ui.sistem_message_area
        self.widget_messages.setLayout(self.message_layout)
        self.ui.sistem_message_area.setWidget(self.widget_messages)#область вывода системных сообщений

        #возможно по нажатию на кнопки стоит создавать потоки и объекты выполнения к ним

        # создадим поток для функции авторизации SeleniumWorkerLogin.login()
        self.thread_login = QtCore.QThread()
        # создадим объект для выполнения кода авторизации в другом потоке
        self.worker_login = SeleniumWorkerLogin(self, username, password)
        # перенесём объект авторизации в другой поток
        self.worker_login.moveToThread(self.thread_login)
        # подключим сигнал старта потока к методу login у объекта, который должен выполнять код в другом потоке
        self.thread_login.started.connect(self.worker_login.login)#отсюда будем конспектировать
        #привязываем нажатие кнопки авторизации к старту потока
        self.ui.autorization_button.clicked.connect(self.thread_login.start)
        self.worker_login.selenium_login.connect(self.alert_message, QtCore.Qt.QueuedConnection)

        self.ui.make_task.clicked.connect(self.run_userpage_task)
        self.ui.delete_unfollow_user.clicked.connect(self.run_userpage_task)
        self.ui.final_delete_users.clicked.connect(self.run_userpage_task)
        self.ui.url_list.itemDoubleClicked.connect(self.get_current_userpage)
        #self.ui.url_list.item

        self.thread_task = None
        self.worker_task = None

    #функция вывода сообщений в нижней части окна приложения
    @QtCore.pyqtSlot(str)
    def alert_message(self, message  = 'Стандартное сообщение'):
        sistem_enter_message = QtWidgets.QLabel(message)
        sistem_enter_message.setWordWrap(True)
        sistem_enter_message.adjustSize()#изменяет размер виджета чтобы соответствовать его содержанию
        self.message_layout.addWidget(sistem_enter_message)
        vbar = self.ui.sistem_message_area.verticalScrollBar()
        vbar.setValue(vbar.maximum())

    #функция заполнения прогресбара
    @QtCore.pyqtSlot(int)
    def progress_value(self, value):
        self.ui.progressBar.setValue(value)

    #функция заполнения списка неподписавшихся на нас пользователей
    @QtCore.pyqtSlot(list)
    def get_unfollowList(self, unfollow_list):
        if len(self.ui.url_list) > 0:#проверка и очистка списка перед новым запуском функции
            self.ui.url_list.clear()
        for link in unfollow_list:
            self.ui.url_list.addItem(link)

    @QtCore.pyqtSlot()
    def clear_url_list(self):#функция очистки списка
        self.ui.url_list.clear()

    #функция отработает в зависимости от того, какая кнопка была нажата
    @QtCore.pyqtSlot()
    def run_userpage_task(self):
        self.thread_task = QtCore.QThread(self)
        self.worker_task = SeleniumWorkerTask(self, username)
        self.worker_task.moveToThread(self.thread_task)
        if self.sender().objectName() == 'make_task':#проверка, какая кнопка была нажата
            self.thread_task.started.connect(self.worker_task.choice_task)
            #дописать логику проверки заполнения поля на введенную ссылку
        elif self.sender().objectName() == 'delete_unfollow_user':#если мы нажали кнопку "удалить неподписавшихся"
            self.thread_task.started.connect(self.worker_task.start_unsubscribe)#запуск сбора списка отписки от пользователей
            self.worker_task.selenium_task_unfollowList.connect(self.get_unfollowList, QtCore.Qt.QueuedConnection)#заполнение списка ссылками на тех, кто на нас не подписался
        elif self.sender().objectName() == 'final_delete_users':#если мы нажали кнопку удалить неподписавшихся
            if len(self.ui.url_list) > 0:
                self.worker_task.unfollow_list = [str(self.ui.url_list.item(i).text()) for i in range(self.ui.url_list.count())]
                self.thread_task.started.connect(self.worker_task.final_delete_users)
                self.worker_task.selenium_task_clearUnfollowList.connect(self.clear_url_list, QtCore.Qt.QueuedConnection)
                self.handleButton()
                return
            
        self.final_workerOperation()

    #функция открытия стрницы по кликнутой в списке ссылке
    @QtCore.pyqtSlot()
    def get_current_userpage(self):
        n = self.ui.url_list.currentRow()
        userpage = self.ui.url_list.item(n).text()
        self.browser.get(userpage)

    #переопределяем стандартную функцию обработки нажатия клавиш клавиатуры
    def keyPressEvent(self, e):
        if len(self.ui.url_list) > 0:
            if e.key() == QtCore.Qt.Key_Delete:
                n = self.ui.url_list.currentRow()
                self.ui.url_list.takeItem(n)#удалит текущий элемент по нажатию клавиши delete, надо написать код на вызов диалоговогоокна


    #спрашиваем, отписаться нам от неподписавшихся на нас пользователей
    def handleButton(self):
        buttonReply = QtWidgets.QMessageBox.question(self, 'Подтверждение удаления', "Удалить неподписавшихся?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,  QtWidgets.QMessageBox.No)
        
        #print(int(buttonReply))
        if buttonReply == QtWidgets.QMessageBox.Yes:
            print('Yes clicked.')
            self.final_workerOperation()#запускаем удаление подписчиков
        if buttonReply == QtWidgets.QMessageBox.No:
            print('No clicked.')
        if buttonReply == QtWidgets.QMessageBox.Cancel:
            print('Cancel')

    @QtCore.pyqtSlot()
    def final_workerOperation(self):
        self.worker_task.selenium_task.connect(self.alert_message, QtCore.Qt.QueuedConnection)
        self.worker_task.selenium_task_progress.connect(self.progress_value, QtCore.Qt.QueuedConnection)
        self.thread_task.start()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    myINSTapp = InstDespadesBot()
    myINSTapp.show()
    sys.exit(app.exec_())
