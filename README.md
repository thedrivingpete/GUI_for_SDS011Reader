# GUI_for_SDS011Reader
A simple GUI for the SDS011 sensor

# Prerequisites
You have to have installed the USB Serial CH340 driver: https://sparks.gogo.co.nz/ch340.html

Also you have to have python installed, for example with Anaconda: https://www.anaconda.com/download/

# Running the GUI
Simply run the script with
`python main_feinstaub.py`

The COM-Port will be asked first. The data is plotted in the window. You can start a measurement, that collects future data, with the rec-button. Also you can save the data that has been collected up to now with the save-button.

# Running the script headless
This is to be used from the shell, for example on a Raspberry Pi via putty (not tested by me). In default, an instance `fs` of the class "Feinstaub" is generated and the function `fs.start()` is called. With this, the data acquisition starts immediately when the script is called. To end the data acquisition, use the function 
`fs.stop()`

The data acquisition can be stated again with 
`fs.start()`

To free the serial connection, use the function
`fs.close()`

All data is saved local in the directory of the script.
