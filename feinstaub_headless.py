# -*- coding: utf-8 -*-
from sds011reader import SDS011Reader
import numpy as np
import time
from sensordummy import SensorDummy
import io
import threading 

dummy = False

class RepeatedTimer(object):
    """Hab ich aus dem Internet (https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds-in-python)"""
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.start()
    
    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

      
    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

class Feinstaub():
    """Die Hauptklasse"""

    def __init__(self, port = "COM5"):
        """
        Die Init-Routine wird aufgerufen beim Erstellen einer Instanz der Klasse.
        Es wird ein Sensor verbunden und mit dem Befehl start() angefangen zu messen.
        Beendet wird die Messung wieder mit der Funktion stop()
        """       
        if dummy: 
            self.sensor = SensorDummy()
        else:
            self.sensor = SDS011Reader(port)
        print("Test, ob verbunden:")
        print(self.sensor.readValue())
        self.data = np.array([0,0,0])# Datenstruktur
        self.startzeit = time.time() # Startzeit der Darstellung
        
    def start(self, intervall = 1, kommentar = ""):
        """
        Startet die Datenaufzeichnung mit einem Datenpunkt pro Intervall [s]
        Es kann ein Kommentar übergeben werden, der dann in der Datei vermerkt wird
        """
        self.run = True
        self.startzeit = time.time() #Setzen der Startzeit
        self.startzeitstr = time.strftime("%Y.%m.%d-%H.%M.%S")
        self.kommentar = kommentar
        #Jetzt noch den ersten Datenpunkt setzen
        values = self.sensor.readValue()
        self.data = np.array([0, values[0], values[1]])
        self.timer = RepeatedTimer(1, self.update) # it auto-starts, no need of timer.start()
        print("Datenaufzeichnung gestartet")
        
    def stop(self):
        """Beendet die Aufzeichnung"""
        if self.run:
            self.run = False
            self.timer.stop()
            self.save()
            
    def update(self):
        """
        Wird von Timer aufgerufen. Holt die Daten vom Sensor
        und schreibt die Daten in die Datenstruktur
        """
        values = self.sensor.readValue()
        t = float(int((time.time()-self.startzeit)*1000))/1000
        #        [pm25,pm10]
        print(t, "s:  2.5mum: ", values[0] ,"mug/m^3  |  10mum: ", values[1] , "mug/m^3")
               
        self.data = np.vstack((self.data, np.array([t, values[0], values[1]])))       
        if len(self.data)%5==0:
            self.save()
        
    def save(self):
        """
        Speichert die aktuell dargestellten Daten in eine Datei mit automatisch
        generiertem Dateinamen im Ordner des Skripts
        """
        data = np.array(self.data[1:])    
        fname = "Feinstaub_" + self.startzeitstr + ".txt" # Der Dateiname
        # Jetzt den Dateiheader zusammenbasteln
        header = time.strftime("%a, %d %b %Y %H:%M:%S") + "\r\n"
        header += fname + "\r\n"
        header += self.kommentar
        header += "\r\n"
        header += "Zeit\tPM2.5\tPM10\r\n"
        header += "s\tmug/m^3\tmug/m^3" #mu, weil str.decode() nicht mit 'µ' klar kommt
        
        print("Speichere Datei...")
#       np.savetxt(datei, data, fmt="%s", delimiter='\t', newline='\r\n', header=header, comments = '')
        # Achtung, jetzt folgt allerübelste Frickelei - Weiterlesen auf eigene Gefahr...
        mem_file = io.BytesIO() # Temporärer Dump für die Ausgabe von savetxt
        np.savetxt(mem_file, data, fmt="%s", delimiter='\t', newline='\r\n', header=header, comments = '') # jetzt die Datei in mem_file schreiben
        new_data_str = mem_file.getvalue().decode().replace('.', ',')# und Punkt durch Komma ersetzen
        new_data_str = new_data_str.replace(fname.replace('.', ','), fname).replace('mu', 'µ') # und jetzt alles reparieren, was ich vorher kaputt gemacht hab
        # und jetzt die eigentliche Datei schreiben
        output_file = open(fname, 'w')
        output_file.write(new_data_str)
        output_file.close()
                    
    def close(self):
        """Schließt die Verbindung mit dem Sensor"""
        self.stop()
        self.sensor.close()
        del self.sensor

if __name__ == '__main__': #Falls das die ausgeführte Datei ist, wird der folgende Teil ausgeführt
    fs = Feinstaub("COM5") #Instanz erzeugen

