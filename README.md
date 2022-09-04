# mmWave Radar data saver

The data saver application is specifically designed to export the data packets returned 
by the [Out-of-Box Demo](https://dev.ti.com/tirex/explore/node?devtools=IWR6843ISK&node=ADSocWGX8FJCytCWREvHzw__VLyFKFf__LATEST)
for the Ti IWR-6843-ISK module. The [frame.py](./Frame.py) file can be manipulated to fit your specific uses.
It is recommended that you change the frame.py file whenever you modify the data return patterns of the mmWave radar.

## Usage instructions
Use [requirements.txt](/requirements.txt) to install the dependencies of the project. 

Run the [UartSave.py](/UartSaver.py) script with the following commandline options:
`python UartSave.py --control_port COM3 --data_port COM6 --output_name test --vis`
to open COM3 as the control port for the mmWave radar, open COM6 as the data receiving port and save all the received
data to a test.pkl file with the data visualiser running

### Commandline Options
The tool has the following commandline options:
* **--control_port**: This argument specifies the COM port to be used to configure the mmWave device.
* **--data_port**: This argument specifies the COM port where we should listen for the data.
* **--output_name**: This argument specifies the filename of the exported file which contains all the data received.
* **--vis**: This argument's presence specifies if we want to run the visualisation

# mmWave Radar Data replayer - PklReader

The data replayer application is designed to play the data stored by the data saver (stored in a `.pkl`) file. This uses
the [Frame.py](/Frame.py) file as well to deduce the data being read.

### Commandline Options
The tool has the following options:
* **--file**: This argument specifies the file name of the file to be read
* **--sim**: This argument forces the replayed to simulate frame processing for a better debugging experience


# Multi-media data saver
The tool has the following commandline options:

* **--control_port**: This argument specifies the COM port to be used to configure the mmWave device.
* **--data_port**: This argument specifies the COM port where we should listen for the data.
* **--output_name**: This argument specifies the filename of the exported file which contains all the data received.
* **--prof**: 

# SerialInterface
This class is an internal class which builds out the communication buffers and provides R/W functionalities to the mmWave
devices.
The class is appropriately annotated and very readable.

# SerialReader
This class is specifically for buffering and reading from a com port and annotating the data. It's self-contained and
requires the following arguments:
* **--file**: CSV file to write out the stored OR live serial data to be converted into a CSV file with the 2D format:
  * time, frame_number, object_number, x, y, z, doppler

# PklExporter
This module is built to export pre-existing pkl style data into CSVs.
It requires the following arguments:
* **--file**: Name of CSV file to write out to.

# NavPlot
This module is built to render the various detected mmWave objects into graphed 3D space.
It's self-contained and can be changed to modified how the graph appears.
This is currently the buggiest of all the modules and is only accessible through various **--vis** arguments
in the other modules.