import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QIcon
from sds011reader import SDS011Reader
import numpy as np
import time
import pyqtgraph as pg
from sensordummy import SensorDummy

dummy = False

class MyWindow(QtWidgets.QMainWindow):
    """Die Klasse des Hauptfensters. Erbt von QMainWindow"""

    def __init__(self):
        """Die Init-Routine wird aufgerufen beim Erstellen einer Instanz der Klasse."""
        # Einstellungen für PyQtPlot
        pg.setConfigOption('background', 'w') #weißer Hintergrund
        pg.setConfigOption('foreground', 'k') #schwarze Schrift
        pg.setConfigOptions(antialias=True) # Antialiasing für schöne Plots
        super(MyWindow, self).__init__() # Der Aufruf des Konstruktors der Mutterklasse
        uic.loadUi('window.ui', self) 
        self.show()
        
        self.sensor = None # Platzhalter für die Sensor-Klasse
        
        #Verknüpfung der Buttons mit den Klassenfunktionen
        self.pushButton_connect.clicked.connect(self.connect)
        self.pushButton_play.clicked.connect(self.start)
        self.pushButton_stop.clicked.connect(self.stop)
        self.pushButton_rec.clicked.connect(self.record)
        self.pushButton_save.clicked.connect(self.saveShowData)
        
        #Variablen/Flags
        self.run = False #Flag für laufende Datenabfrage
        self.rec = False #Flag für laufende Datenaufnahme
        self.timer = QtCore.QTimer() #Timer
        self.timer.timeout.connect(self.update) # wird mit der update-Funktion verknüpft
        self.data = np.array([0,0,0])# Datenstruktur für die Darstellung im Fenster
        self.recdata = np.array([0,0,0]) # Datenstruktur für die Aufzeichnung
        self.startzeit = time.time() # Startzeit der Darstellung
        self.startzeit_rec = time.time() #Startzeit der Aufnahme
        self.startzeit_rec_str = time.strftime("%Y.%m.%d-%H.%M.%S") # String der Startzeit der Aufnahme
        
        self.plot = self.graphicsView_plot.getPlotItem() #Das PlotItem in der Oberfläche       
        
        self.plot.showGrid(x=True, y=True) # Zeige das Gitter
        self.kurve25 = self.plot.plot(pen='k', symbol = None) #Die Kurve für 2.5mum
        self.kurve10 = self.plot.plot(pen='r', symbol = None) #Die Kurve für 10mum
        self.plot.setLabel('left', "PM", units="<html>&mu;g/m<sup>3</sup></html>") #Setze die y-Achse
        self.plot.setLabel('bottom', "Zeit", units='s') #Setze die x-Achse
        self.plot.setLimits(xMin=0) #Lässt den Plot links immer bei 0 anfangen
        self.groupBox_rec.setVisible(False)
        self.pushButton_play.setVisible(False)
        self.pushButton_rec.setVisible(False)
        self.pushButton_stop.setVisible(False)
        self.graphicsView_plot.setVisible(False)
        self.groupBox_display.setVisible(False)
        self.pushButton_save.setVisible(False)
        
    def connect(self):
        """Legt eine Instanz der Sensorklasse an. Verwendet den im GUI eingestellten COM-Port"""
        print("Verbinde mit Sensor...")
        if dummy: 
            self.sensor = SensorDummy()
        else:
            self.sensor = SDS011Reader(self.lineEdit_com.text())
        print("Test, ob verbunden:")
        print(self.sensor.readValue())
        #Anzeige des Rests der GUI
        self.groupBox_connect.setVisible(False)
        self.groupBox_rec.setVisible(True)
        self.pushButton_play.setVisible(True)
        self.pushButton_rec.setVisible(True)
        self.pushButton_stop.setVisible(True)
        self.graphicsView_plot.setVisible(True)
        self.groupBox_display.setVisible(True)
        self.pushButton_save.setVisible(True)
        self.start()
        
    def start(self):
        """Startet die Datenabfrage und die Darstellung der Daten"""
        print("Start geclicked")
        self.run = True
        self.pushButton_play.setIcon(QIcon('gui//play_on.png')) #Icon auf Grünen Pfeil ändern
        self.timer.start(1000) #Abfrage alle 1000ms
        self.startzeit = time.time() #Setzen der Startzeit
        #Jetzt noch den ersten Datenpunkt setzen
        values = self.sensor.readValue()
        self.data = np.array([0, values[0], values[1]])
        
    def stop(self):
        """Beendet die Aufzeichnung und die Darstellung"""
        print("Stop geclicked")
        if self.rec:
            self.save_rec()
            self.rec = False
            self.pushButton_rec.setIcon(QIcon('gui//rec.png'))
        if self.run:
            self.run = False
            self.timer.stop()
            self.pushButton_play.setIcon(QIcon('gui//play.png'))
    
    def record(self):
        """Beginnt die Aufzeichnung in eine Datei"""
        print("rec geclickt")
        if not self.rec:
            if not self.run:
                self.start()
            pfad  = QtWidgets.QFileDialog.getExistingDirectory(self,
                    "Ordner zum Speichern setzen...",
                    "", options=QtWidgets.QFileDialog.ShowDirsOnly)
            if pfad:
                self.ordner = pfad
                self.startzeit_rec_str = time.strftime("%Y.%m.%d-%H.%M.%S")
                self.lineEdit_ordner.setText(self.ordner)
                self.rec = True
                self.pushButton_rec.setIcon(QIcon('gui\\rec_on.png'))
                #Jetzt noch den ersten Datenpunkt setzen
                values = self.sensor.readValue()
                self.recdata = np.array([0, values[0], values[1]])
        else:
            self.save_rec()            
            self.rec = False
        
    def update(self):
        """
        Wird von Timer aufgerufen. Holt die daten vom Sensor, stellt sie dar 
        und schreibt die Daten in die Datenstrukturen
        """
        values = self.sensor.readValue()
        t = float(int((time.time()-self.startzeit)*1000))/1000
        #        [pm25,pm10]
        print(t, "s:  2.5mum: ", values[0] ,"mug/m^3  |  10mum: ", values[1] , "mug/m^3")
        self.label_display25.setText(self.textFormat(values[0]))
        self.label_display10.setText(self.textFormat(values[1]))
               
        self.data = np.vstack((self.data, np.array([t, values[0], values[1]])))
        if max(self.data[:,0])>18000:
            self.plot.setLabel('bottom', "Zeit", units='h') #Setze die x-Achse
            self.kurve25.setData(self.data[:,0]/3600, self.data[:,1])
            self.kurve10.setData(self.data[:,0]/3600, self.data[:,2])
        elif max(self.data[:,0])>300:
            self.plot.setLabel('bottom', "Zeit", units='min') #Setze die x-Achse
            self.kurve25.setData(self.data[:,0]/60, self.data[:,1])
            self.kurve10.setData(self.data[:,0]/60, self.data[:,2])
        else:
            self.plot.setLabel('bottom', "Zeit", units='s') #Setze die x-Achse
            self.kurve25.setData(self.data[:,0], self.data[:,1])
            self.kurve10.setData(self.data[:,0], self.data[:,2])
        
        if self.rec:
            t_rec = time.time()-self.startzeit_rec
            self.recdata = np.vstack((self.recdata, np.array([t_rec, values[0], values[1]])))
            if len(self.data)%5==0:
                self.save_rec()
                
    def textFormat(self, value):
        text =  "<html><head/><body><p><span style=\"font-size:11pt;"
        text += "font-weight:600; color:#aa0000;\">" + str(value)
        text += " µg/m</span><span style=\" font-size:11pt; font-weight:600;"
        text += "color:#aa0000; vertical-align:super;\">3</span></p></body></html>"
        return text
                
    def save_rec(self):
        data = np.array(self.recdata[1:])

        fname = "Feinstaub_" + self.startzeit_rec_str + ".fs"
                
        header = time.strftime("%a, %d %b %Y %H:%M:%S") + "\r\n"
        header += fname + "\r\n"
        header += self.lineEdit_kommentar.text()
        header += "\r\n"
#                 winkel,  P,        signal,        RMS_signal,    T_mess,    U_mess,    U_qcl,    I_av,    I_p_calc,       I_p_oszi  
        header += "Zeit\tPM2.5\tPM10\r\n"
        header += "s\t#/m^3\t#/m^3" 
        
        datei = self.ordner + "\\" + fname
        print("Speichere Datei...")
        np.savetxt(datei, data, fmt="%s", delimiter='\t', newline='\r\n', header=header, comments = '')
        
    def saveShowData(self):
        pfad  = QtWidgets.QFileDialog.getExistingDirectory(self,
                "Ordner zum Speichern setzen...",
                "", options=QtWidgets.QFileDialog.ShowDirsOnly)
        if pfad:
            data = np.array(self.data[1:])    
            fname = "Feinstaub_" + time.strftime("%Y.%m.%d-%H.%M.%S") + ".fs"
                    
            header = time.strftime("%a, %d %b %Y %H:%M:%S") + "\r\n"
            header += fname + "\r\n"
            header += self.lineEdit_kommentar.text()
            header += "\r\n"
    #                 winkel,  P,        signal,        RMS_signal,    T_mess,    U_mess,    U_qcl,    I_av,    I_p_calc,       I_p_oszi  
            header += "Zeit\tPM2.5\tPM10\r\n"
            header += "s\t#/m^3\t#/m^3" 
            
            datei = pfad + "\\" + fname
            print("Speichere Datei...")
            np.savetxt(datei, data, fmt="%s", delimiter='\t', newline='\r\n', header=header, comments = '')
                    
    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Wirklich beenden?',
            "Wirklich beenden?", QtWidgets.QMessageBox.Yes | 
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            try:
                self.stop()
                self.sensor.close()
                del self.sensor
            except:
                pass
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    from PyQt5.QtGui import QApplication 
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance() 
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
