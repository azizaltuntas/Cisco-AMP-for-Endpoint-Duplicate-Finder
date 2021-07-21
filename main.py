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

            if self.inputApiFQDN.text() == "" or self.inputClientId.text() == "" or self.inputApiKey.text() == "":

                self.alert("Input Error","Please enter all settings!")

            else:

                self.headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8','accept': 'application/json','Accept-Encoding': 'gzip'}

                self.url = 'http://{0}:{1}@{2}/v1/version'.format(self.inputApiFQDN.text(),self.inputClientId.text(),self.inputApiKey.text())

                self.req = requests.get(self.url, headers=self.headers)
                

                if self.req.status_code == 401:
                    self.alert("Connection","Wrong Api Key or Client ID!")

                elif self.req.status_code == 200:
                    self.alert("Connection","Connection successful!")
                    self.LoadComputersButton.setEnabled(True)


        except Exception as e:
            self.alert("Warning","Connection error!")

    def deleteComputer(self,guid):

        try:

            self.deleteurl = "https://{0}:{1}@{2}/v1/computers/{3}".format(self.inputApiFQDN.text(),self.inputClientId.text(),self.inputApiKey.text(),guid)

            self.delreq = requests.delete(self.deleteurl,headers=self.headers)
            self.deljson = self.delreq.json()

            if str(self.deljson['data']['deleted']) == "True":
                self.DeleteDuplicatesArea.addItem(guid+" : "+"Deleted!")
            else:
                self.DeleteDuplicatesArea.addItem(guid+" : "+"Not deleted!")

        except Exception as f:

            t, o, tb = sys.exc_info()
            self.DeleteDuplicatesArea.addItem(guid+" : "+"Not deleted!")
            print(f,tb.tb_lineno)            


    def runSendDelete(self):

        for i in range(self.DeleteDuplicatesArea.count()):
            thread = threading.Thread(target=self.deleteComputer,args=(self.DeleteDuplicatesArea.item(i).text(),))
            thread.daemon = True
            thread.start()

    def sendDelete(self):

        thread = threading.Thread(target=self.runSendDelete)
        thread.start()


    def threadFunc(self,qu,qu2):

        try:
            
            self.url = 'http://{0}:{1}@{2}/v1/computers?offset='.format(self.inputApiFQDN.text(),self.inputClientId.text(),self.inputApiKey.text())

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

                self.inputAllComputersTotal.setText(str(self.s)+" Computer")
                self.LoadDuplicatesButton.setEnabled(True)

        except Exception as f:

            t, o, tb = sys.exc_info()
            print(f,tb.tb_lineno)

    def start(self):

    	if not self.totallist:

	        thread = threading.Thread(target=self.startfunc)
	        thread.start()

    def startfunc(self):

        try:

            self.url2 = 'http://{0}:{1}@{2}/v1/computers'.format(self.inputApiFQDN.text(),self.inputClientId.text(),self.inputApiKey.text())
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

                self.get = 'http://{0}:{1}@{2}/v1/computers?hostname[]='.format(self.inputApiFQDN.text(),self.inputClientId.text(),self.inputApiKey.text())


                self.req = requests.get(self.get+str(self.gek),headers=self.headers)
                self.getjson = self.req.json()
                self.cse = QtWidgets.QTreeWidgetItem(self.DuplicateComputersArea)

                for getfull in self.getjson['data']:

                    count += 1

                    self.esc = self.cse.setText(0,getfull['hostname'])
                    self.cse.setText(1,str(count))
                    self.cse.setText(2,getfull['policy']['name'])

                    self.item = QtWidgets.QTreeWidgetItem(self.cse)

                    self.item.setText(0,"Last Seen: "+getfull['last_seen']+"\n"+"GUID: "+getfull['connector_guid']+"\n"+"Version: "+getfull['connector_version'])

                    
                hosts.task_done()

                
                self.inputDuplicateComputersTotal.setText(str(len(self.duplicatelist))+" Duplicate")


                count = 0
        except Exception as f:

            t, o, tb = sys.exc_info()
            print(f,tb.tb_lineno)

    def RunGetDuplicate(self):

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


    def GetDuplicate(self):
        thread = threading.Thread(target=self.RunGetDuplicate)
        thread.start()

    def olurmu(self):

        #Seçilen itemlerin yazıldığı fonksiyon

        fullitems = self.DuplicateComputersArea.selectedItems()
        
        if fullitems:
            base = fullitems[0]
            reitems = base.text(0)

            reitems = reitems.split()
            for i in reitems:
                if re.findall(r'[a-z0-9]{8}[-][a-z0-9]{4}[-][a-z0-9]{4}[-][a-z0-9]{4}[-][a-z0-9]{12}',i):
                    itemsList =  [str(self.DeleteDuplicatesArea.item(l).text()) for l in range(self.DeleteDuplicatesArea.count())]
                    if i in itemsList:
                        None
                    else:
                        self.b += 1
                        self.DeleteDuplicatesArea.addItem(i)
                        self.inputDeleteDuplicateTotal.setText(str(self.b))
                        self.DeleteDuplicatesButton.setEnabled(True)


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(1120, 749) #resize
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1120, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.SettingsAreaGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.SettingsAreaGroup.setGeometry(QtCore.QRect(20, 20, 381, 151))
        self.SettingsAreaGroup.setObjectName("SettingsAreaGroup")
        self.labelApiFQDN = QtWidgets.QLabel(self.SettingsAreaGroup)
        self.labelApiFQDN.setGeometry(QtCore.QRect(20, 30, 70, 13))
        self.labelApiFQDN.setObjectName("labelApiFQDN")
        self.labelClientId = QtWidgets.QLabel(self.SettingsAreaGroup)
        self.labelClientId.setGeometry(QtCore.QRect(20, 60, 70, 13))
        self.labelClientId.setObjectName("labelClientId")
        self.labelApiKey = QtWidgets.QLabel(self.SettingsAreaGroup)
        self.labelApiKey.setGeometry(QtCore.QRect(20, 90, 70, 13))
        self.labelApiKey.setObjectName("labelApiKey")
        self.inputApiFQDN = QtWidgets.QLineEdit(self.SettingsAreaGroup)
        self.inputApiFQDN.setGeometry(QtCore.QRect(100, 60, 251, 20))
        self.inputApiFQDN.setObjectName("inputApiFQDN")
        self.inputClientId = QtWidgets.QLineEdit(self.SettingsAreaGroup)
        self.inputClientId.setGeometry(QtCore.QRect(100, 90, 251, 20))
        self.inputClientId.setObjectName("inputClientId")
        self.inputApiKey = QtWidgets.QLineEdit(self.SettingsAreaGroup)
        self.inputApiKey.setGeometry(QtCore.QRect(100, 30, 251, 20))
        self.inputApiKey.setObjectName("inputApiKey")
        self.TestConnectionButton = QtWidgets.QPushButton(self.SettingsAreaGroup)
        self.TestConnectionButton.setGeometry(QtCore.QRect(100, 120, 120, 23))
        self.TestConnectionButton.setObjectName("TestConnectionButton")
        self.LoadComputersButton = QtWidgets.QPushButton(self.SettingsAreaGroup)
        self.LoadComputersButton.setGeometry(QtCore.QRect(220, 120, 120, 23))
        self.LoadComputersButton.setObjectName("LoadComputersButton")
        self.LoadComputersButton.setEnabled(False)

        self.AllComputersAreaGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.AllComputersAreaGroup.setGeometry(QtCore.QRect(20, 180, 531, 521))
        self.AllComputersAreaGroup.setObjectName("AllComputersAreaGroup")
        self.AllComputersArea = QtWidgets.QTreeWidget(self.AllComputersAreaGroup)
        self.AllComputersArea.setGeometry(QtCore.QRect(10, 30, 511, 445))
        self.AllComputersArea.setObjectName("AllComputersArea")
        self.AllComputersArea.headerItem().setText(0, "Hostname")
        self.labelTotalComputers = QtWidgets.QLabel(self.AllComputersAreaGroup)
        self.labelTotalComputers.setGeometry(QtCore.QRect(120, 480, 71, 16))
        self.labelTotalComputers.setObjectName("labelTotalComputers")
        self.inputAllComputersTotal = QtWidgets.QLineEdit(self.AllComputersAreaGroup)
        self.inputAllComputersTotal.setGeometry(QtCore.QRect(200, 480, 113, 20))
        self.inputAllComputersTotal.setObjectName("inputAllComputersTotal")
        self.inputAllComputersTotal.setReadOnly(True)
                
        self.DuplicateComputersAreaGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.DuplicateComputersAreaGroup.setGeometry(QtCore.QRect(560, 20, 541, 405))
        self.DuplicateComputersAreaGroup.setObjectName("DuplicateComputersAreaGroup")
        self.DuplicateComputersArea = QtWidgets.QTreeWidget(self.DuplicateComputersAreaGroup)
        self.DuplicateComputersArea.setGeometry(QtCore.QRect(10, 30, 521, 335))
        self.DuplicateComputersArea.setObjectName("DuplicateComputersArea")
        self.LoadDuplicatesButton = QtWidgets.QPushButton(self.DuplicateComputersAreaGroup)
        self.LoadDuplicatesButton.setGeometry(QtCore.QRect(50, 370, 131, 23))
        self.LoadDuplicatesButton.setObjectName("LoadDuplicatesButton")
        self.LoadDuplicatesButton.setEnabled(False)
        self.labelTotalDuplicateComputers = QtWidgets.QLabel(self.DuplicateComputersAreaGroup)
        self.labelTotalDuplicateComputers.setGeometry(QtCore.QRect(230, 370, 71, 16))
        self.labelTotalDuplicateComputers.setObjectName("labelTotalDuplicateComputers")
        self.inputDuplicateComputersTotal = QtWidgets.QLineEdit(self.DuplicateComputersAreaGroup)
        self.inputDuplicateComputersTotal.setGeometry(QtCore.QRect(310, 370, 113, 20))
        self.inputDuplicateComputersTotal.setObjectName("inputDuplicateComputersTotal")
        self.inputDuplicateComputersTotal.setReadOnly(True)

        self.DeleteDuplicatesAreaGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.DeleteDuplicatesAreaGroup.setGeometry(QtCore.QRect(560, 440, 541, 261))
        self.DeleteDuplicatesAreaGroup.setObjectName("DeleteDuplicatesAreaGroup")
        self.DeleteDuplicatesArea = QtWidgets.QListWidget(self.DeleteDuplicatesAreaGroup)
        self.DeleteDuplicatesArea.setGeometry(QtCore.QRect(10, 25, 521, 192))
        self.DeleteDuplicatesArea.setObjectName("DeleteDuplicatesArea")
        self.DeleteDuplicatesButton = QtWidgets.QPushButton(self.DeleteDuplicatesAreaGroup)
        self.DeleteDuplicatesButton.setGeometry(QtCore.QRect(50, 220, 131, 23))
        self.DeleteDuplicatesButton.setObjectName("DeleteDuplicatesButton")
        self.DeleteDuplicatesButton.setEnabled(False)
        self.labelTotalComputersForDeletion = QtWidgets.QLabel(self.DeleteDuplicatesAreaGroup)
        self.labelTotalComputersForDeletion.setGeometry(QtCore.QRect(230, 220, 71, 16))
        self.labelTotalComputersForDeletion.setObjectName("labelTotalComputersForDeletion")
        self.inputDeleteDuplicateTotal = QtWidgets.QLineEdit(self.DeleteDuplicatesAreaGroup)
        self.inputDeleteDuplicateTotal.setGeometry(QtCore.QRect(310, 220, 113, 20))
        self.inputDeleteDuplicateTotal.setObjectName("inputDeleteDuplicateTotal")
        self.inputDeleteDuplicateTotal.setReadOnly(True)
        
        

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
        self.TestConnectionButton.clicked.connect(self.function)
        self.LoadComputersButton.clicked.connect(self.start)
        self.LoadDuplicatesButton.clicked.connect(self.GetDuplicate)
        self.DuplicateComputersArea.itemDoubleClicked.connect(self.olurmu)
        self.DeleteDuplicatesButton.clicked.connect(self.sendDelete)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AMP for Endpoints Duplicate Finder"))
        self.AllComputersAreaGroup.setTitle(_translate("MainWindow", "Computers"))
        self.AllComputersArea.headerItem().setText(1, _translate("MainWindow", "Connector Version"))
        self.AllComputersArea.headerItem().setText(2, _translate("MainWindow", "Policy Name"))
        self.AllComputersArea.headerItem().setText(3, _translate("MainWindow", "Connector ID"))
        self.AllComputersArea.headerItem().setText(4, _translate("MainWindow", "Operation System"))
        self.labelTotalComputers.setText(_translate("MainWindow", "Total #"))
        self.SettingsAreaGroup.setTitle(_translate("MainWindow", "Connection settings"))
        self.labelClientId.setText(_translate("MainWindow", "Client ID:"))
        self.labelApiKey.setText(_translate("MainWindow", "API Key:"))
        self.TestConnectionButton.setText(_translate("MainWindow", "Test connection"))
        self.LoadComputersButton.setText(_translate("MainWindow", "Load computers"))
        self.labelApiFQDN.setText(_translate("MainWindow", "API FQDN:"))
        self.DuplicateComputersAreaGroup.setTitle(_translate("MainWindow", "Duplicate computers"))
        self.DuplicateComputersArea.headerItem().setText(0, _translate("MainWindow", "Computer"))
        self.DuplicateComputersArea.headerItem().setText(1, _translate("MainWindow", "Count"))
        self.DuplicateComputersArea.headerItem().setText(2, _translate("MainWindow", "Policy Name"))

        __sortingEnabled = self.DuplicateComputersArea.isSortingEnabled()
        self.DuplicateComputersArea.setSortingEnabled(False)
        self.DuplicateComputersArea.setSortingEnabled(__sortingEnabled)
        self.LoadDuplicatesButton.setText(_translate("MainWindow", "Load duplicates"))
        self.labelTotalDuplicateComputers.setText(_translate("MainWindow", "Total #"))
        self.labelTotalComputersForDeletion.setText(_translate("MainWindow", "Total #"))
        self.DeleteDuplicatesAreaGroup.setTitle(_translate("MainWindow", "Computers for deletion"))
        self.DeleteDuplicatesButton.setText(_translate("MainWindow", "Delete computers"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('gtk+')
    #app.setStyleSheet("b")
    win = Ui_Dialog()
    cls = QMainWindow()
    win.setupUi(cls)
    cls.show()
    sys.exit(app.exec_())
