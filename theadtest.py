import sys
import time
 
from PyQt5 import QtCore, QtWidgets
from selenium import webdriver

class SeleniumWorker(QtCore.QObject):
    progressChanged = QtCore.pyqtSignal(int)
    def do_work(self):
        progress = 0
        browser = webdriver.Chrome('./drivers/chromedriver')
        links = ['https://www.youtube.com/c/PythonToday/videos',
        'https://evileg.com/ru/post/579/',
        'https://vk.com/olya_lykoya']
        for link in links:
            browser.get(link)
            progress += 100 / len(links)
            self.progressChanged.emit(progress)
            time.sleep(10)
        browser.close()


class Widget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        lay = QtWidgets.QHBoxLayout(self)
        progressBar = QtWidgets.QProgressBar()
        progressBar.setRange(0, 100)
        button = QtWidgets.QPushButton("Start")
        lay.addWidget(progressBar)
        lay.addWidget(button)
        self.thread = QtCore.QThread()
        self.worker = SeleniumWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.do_work)
        button.clicked.connect(self.thread.start)
        self.worker.progressChanged.connect(progressBar.setValue, QtCore.Qt.QueuedConnection)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())
 
 
