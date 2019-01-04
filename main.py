# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication ,QMainWindow,QMessageBox,QTabWidget,QTreeWidget,QTreeWidgetItem
import sys,re
import urllib3
import json
import requests
import threading
from threading import Thread
from queue import Queue
from collections import Counter
import multiprocessing


class Ui_Dialog(QMainWindow):


    def alert(self,boxerror,abnormal):


        QMessageBox.question(self, boxerror, abnormal, QMessageBox.Ok)


    def function(self):

        try:

            if self.lineEdit.text() == "" or self.lineEdit_2.text() == "" or self.lineEdit_5.text() == "":

                self.alert("Input Error","Please Enter All Settings ! ")

            else:

                self.headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8','accept': 'application/json','Accept-Encoding': 'gzip'}

                self.url = 'http://{0}:{1}@{2}/version'.format(self.lineEdit.text(),self.lineEdit_2.text(),self.lineEdit_5.text())

                self.req = requests.get(self.url, headers=self.headers)
                

                if self.req.status_code == 401:
                    self.alert("Connection","Api Key or Client ID Wrong !")

                elif self.req.status_code == 200:
                    self.alert("Connection","Connection Successfull !")
                    self.pushButton_2.setEnabled(True)


        except Exception as e:
            self.alert("Warning","Connection ERROR !")

    def deleteComputer(self,guid):

        try:

            self.deleteurl = "https://{0}:{1}@{2}/computers/{3}".format(self.lineEdit.text(),self.lineEdit_2.text(),self.lineEdit_5.text(),guid)

            self.delreq = requests.delete(self.deleteurl,headers=self.headers)
            self.deljson = self.delreq.json()

            if str(self.deljson['data']['deleted']) == "True":
                self.listWidget.addItem(guid+" : "+"DELETED !")
            else:
                self.listWidget.addItem(guid+" : "+"NOT DELETED !")

        except Exception as f:

            t, o, tb = sys.exc_info()
            self.listWidget.addItem(guid+" : "+"NOT DELETED !")
            print(f,tb.tb_lineno)            


    def sendDeleteFunc(self):

        for i in range(self.listWidget.count()):
            thread = threading.Thread(target=self.deleteComputer,args=(self.listWidget.item(i).text(),))
            thread.daemon = True
            thread.start()

    def sendDelete(self):

        thread = threading.Thread(target=self.sendDeleteFunc)
        thread.start()


    def threadFunc(self,qu,qu2):

        try:
            
            self.url = 'http://{0}:{1}@{2}/computers?offset='.format(self.lineEdit.text(),self.lineEdit_2.text(),self.lineEdit_5.text())

            while True:


                self.rakam = qu.get()
                self.sayben = qu2.get()

                self.r = requests.get(self.url+str(self.rakam), headers=self.headers)
                self.full = self.r.json()

                for c in self.full['data']:


                    self.sayben += 1
                    self.s += 1

                    self.items = QtWidgets.QTreeWidgetItem(self.treeWidget)
                    print(c['hostname']+str(self.s))
                    self.esc = self.items.setText(0,c['hostname'])


                    self.items.setText(1,c['connector_version'])
                    self.items.setText(2,c['policy']['name'])
                    self.items.setText(3,c['connector_guid'])
                    self.items.setText(4,c['operating_system'])

                    self.totallist.append(c['hostname'])
                    self.guid.append(c['connector_guid'])
                    self.lastseen.append(c['last_seen'])
                    self.deneme[c['connector_guid']] = c['last_seen']



                qu.task_done()
                qu2.task_done()

                self.lineEdit_3.setText(str(self.s)+" Computer")
                self.pushButton_3.setEnabled(True)

        except Exception as f:

            t, o, tb = sys.exc_info()
            print(f,tb.tb_lineno)

    def start(self):

    	if not self.totallist:

	        thread = threading.Thread(target=self.startfunc)
	        thread.start()

    def startfunc(self):

        try:

            self.url2 = 'http://{0}:{1}@{2}/computers'.format(self.lineEdit.text(),self.lineEdit_2.text(),self.lineEdit_5.text())
            self.req = requests.get(self.url2, headers=self.headers)
            self.full2 = self.req.json()

            self.total = self.full2['metadata']['results']['total']
            self.total = int(self.total)
            self.total2 = round(self.total/500)

            self.la = 0
            self.say = 0
            self.on = 0




            for i in range(self.total2+1):

                thread = threading.Thread(target=self.threadFunc,args=(self.sira,self.sira2,))
                thread.daemon = True
                thread.start()

            for g in range(10):
                self.sira.put(self.la)

                self.la += 500

            for b in range(10):
                self.sira2.put(self.say)
                self.say += 500


            self.sira.join()
            self.sira2.join()


        except Exception as f:

            t, o, tb = sys.exc_info()
            print(f,tb.tb_lineno)

    def dublicate(self,hosts):
        try:

            count = 0

            while True:

                self.gek = hosts.get()

                self.get = 'http://{0}:{1}@{2}/computers?hostname[]='.format(self.lineEdit.text(),self.lineEdit_2.text(),self.lineEdit_5.text())


                self.req = requests.get(self.get+str(self.gek),headers=self.headers)
                self.getjson = self.req.json()
                self.cse = QtWidgets.QTreeWidgetItem(self.treeWidget_2)

                for getfull in self.getjson['data']:

                    count += 1

                    self.esc = self.cse.setText(0,getfull['hostname'])
                    self.cse.setText(1,str(count))
                    self.cse.setText(2,getfull['policy']['name'])

                    self.item = QtWidgets.QTreeWidgetItem(self.cse)

                    self.item.setText(0,"Last Seen: "+getfull['last_seen']+"\n"+"C-GUID: "+getfull['connector_guid']+"\n"+"C-Version: "+getfull['connector_version'])

                    
                hosts.task_done()

                
                self.lineEdit_4.setText(str(len(self.duplicatelist))+" Duplicate")


                count = 0
        except Exception as f:

            t, o, tb = sys.exc_info()
            print(f,tb.tb_lineno)

    def getdublicatefunc(self):

        try:

        	if not self.duplicatelist:

	            c = Counter(c.strip() for c in self.totallist if c.strip())

	            for line in c:
	                if c[line]>1:
	                    self.duplicatelist.append(line)
	                    self.on += c[line]

	            for h in range(4):

	                thread = threading.Thread(target=self.dublicate, args=(self.dup,))
	                thread.daemon = True
	                thread.start()


	            for starw in self.duplicatelist:
	                self.dup.put(starw)


	            self.dup.join()
	        else:
	        	None

        except Exception as f:

            t, o, tb = sys.exc_info()
            print(f,tb.tb_lineno)


    def getdublicate(self):
        thread = threading.Thread(target=self.getdublicatefunc)
        thread.start()

    def olurmu(self):

        #Seçilen itemlerin yazıldığı fonksiyon

        fullitems = self.treeWidget_2.selectedItems()
        
        if fullitems:
            base = fullitems[0]
            reitems = base.text(0)

            reitems = reitems.split()
            for i in reitems:
                if re.findall(r'[a-z0-9]{8}[-][a-z0-9]{4}[-][a-z0-9]{4}[-][a-z0-9]{4}[-][a-z0-9]{12}',i):
                    itemsList =  [str(self.listWidget.item(l).text()) for l in range(self.listWidget.count())]
                    if i in itemsList:
                        None
                    else:
                        self.b += 1
                        self.listWidget.addItem(i)
                        self.lineEdit_6.setText(str(self.b))
                        self.pushButton_4.setEnabled(True)


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1120, 749)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(20, 180, 531, 521))
        self.groupBox.setObjectName("groupBox")
        self.treeWidget = QtWidgets.QTreeWidget(self.groupBox)
        self.treeWidget.setGeometry(QtCore.QRect(10, 40, 511, 421))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "Hostname")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(120, 480, 71, 16))
        self.label_3.setObjectName("label_3")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_3.setGeometry(QtCore.QRect(200, 480, 113, 20))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 20, 381, 151))
        self.groupBox_2.setObjectName("groupBox_2")
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit.setGeometry(QtCore.QRect(100, 60, 251, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_2.setGeometry(QtCore.QRect(100, 90, 251, 20))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(20, 60, 47, 13))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(20, 90, 47, 13))
        self.label_2.setObjectName("label_2")
        self.pushButton = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton.setGeometry(QtCore.QRect(120, 120, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_2.setGeometry(QtCore.QRect(244, 120, 81, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setGeometry(QtCore.QRect(20, 30, 47, 13))
        self.label_5.setObjectName("label_5")
        self.lineEdit_5 = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_5.setGeometry(QtCore.QRect(100, 30, 251, 20))
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(560, 20, 541, 341))
        self.groupBox_3.setObjectName("groupBox_3")
        self.treeWidget_2 = QtWidgets.QTreeWidget(self.groupBox_3)
        self.treeWidget_2.setGeometry(QtCore.QRect(10, 30, 521, 241))
        self.treeWidget_2.setObjectName("treeWidget_2")
        self.lineEdit_3.setReadOnly(True)


        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_3.setGeometry(QtCore.QRect(50, 290, 131, 23))
        self.pushButton_3.setObjectName("pushButton_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setGeometry(QtCore.QRect(230, 290, 71, 16))
        self.label_4.setObjectName("label_4")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox_3)
        self.lineEdit_4.setGeometry(QtCore.QRect(310, 290, 113, 20))
        self.lineEdit_4.setObjectName("lineEdit_4")



        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(560, 380, 541, 261))
        self.groupBox_4.setObjectName("groupBox_4")

        self.lineEdit_6 = QtWidgets.QLineEdit(self.groupBox_4)
        self.lineEdit_6.setGeometry(QtCore.QRect(310, 220, 113, 20))
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.lineEdit_6.setReadOnly(True)

        self.label_6 = QtWidgets.QLabel(self.groupBox_4)
        self.label_6.setGeometry(QtCore.QRect(230, 220, 71, 16))
        self.label_6.setObjectName("label_6")

        self.listWidget = QtWidgets.QListWidget(self.groupBox_4)
        self.listWidget.setGeometry(QtCore.QRect(10, 20, 521, 192))
        self.listWidget.setObjectName("listWidget")
        self.pushButton_4 = QtWidgets.QPushButton(self.groupBox_4)
        self.pushButton_4.setGeometry(QtCore.QRect(50, 220, 131, 23))
        self.pushButton_4.setObjectName("pushButton_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1120, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.lineEdit_4.setReadOnly(True)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(False)


        self.headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8','accept': 'application/json','Accept-Encoding': 'gzip'}


        self.sira = Queue()
        self.sira2 = Queue()

        self.dup = Queue()

        self.totallist = list()
        self.guid = list()
        self.lastseen = list()
        self.duplicatelist = list()

        self.deneme = {}
        self.s = 0
        self.b = 0

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.pushButton.clicked.connect(self.function)
        self.pushButton_2.clicked.connect(self.start)
        self.pushButton_3.clicked.connect(self.getdublicate)
        self.treeWidget_2.itemDoubleClicked.connect(self.olurmu)
        self.pushButton_4.clicked.connect(self.sendDelete)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AMP for Endpoints Duplicate Finder"))
        self.groupBox.setTitle(_translate("MainWindow", "ALL Computers"))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "Connector Version"))
        self.treeWidget.headerItem().setText(2, _translate("MainWindow", "Policy Name"))
        self.treeWidget.headerItem().setText(3, _translate("MainWindow", "Connector ID"))
        self.treeWidget.headerItem().setText(4, _translate("MainWindow", "Operation System"))
        self.label_3.setText(_translate("MainWindow", "Total Number :"))
        self.groupBox_2.setTitle(_translate("MainWindow", "API Connection Settings"))
        self.label.setText(_translate("MainWindow", "Client ID :"))
        self.label_2.setText(_translate("MainWindow", "Api Key :"))
        self.pushButton.setText(_translate("MainWindow", "Test Connect"))
        self.pushButton_2.setText(_translate("MainWindow", "Get Computers"))
        self.label_5.setText(_translate("MainWindow", "Api Url :"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Duplicate Computers"))
        self.treeWidget_2.headerItem().setText(0, _translate("MainWindow", "Computers"))
        self.treeWidget_2.headerItem().setText(1, _translate("MainWindow", "Count"))
        self.treeWidget_2.headerItem().setText(2, _translate("MainWindow", "Policy Name"))

        __sortingEnabled = self.treeWidget_2.isSortingEnabled()
        self.treeWidget_2.setSortingEnabled(False)
        self.treeWidget_2.setSortingEnabled(__sortingEnabled)
        self.pushButton_3.setText(_translate("MainWindow", "Get Information"))
        self.label_4.setText(_translate("MainWindow", "Total Number :"))
        self.label_6.setText(_translate("MainWindow", "Total Number :"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Delete Computers"))
        self.pushButton_4.setText(_translate("MainWindow", "Delete Computers"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('gtk+')
    app.setStyleSheet("b")
    win = Ui_Dialog()
    cls = QMainWindow()
    win.setupUi(cls)
    cls.show()
    sys.exit(app.exec_())
