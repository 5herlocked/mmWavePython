# mmWave Radar data saver

The data saver application is specifically designed to export the data packets returned 
by the [Out-of-Box Demo](https://dev.ti.com/tirex/explore/node?devtools=IWR6843ISK&node=ADSocWGX8FJCytCWREvHzw__VLyFKFf__LATEST)
for the Ti IWR-6843-ISK module. The [frame.py](./Frame.py) file can be manipulated to fit your specific uses.
It is recommended that you change the frame.py file whenever you modify the data return patterns of the mmWave radar.

### Commandline Options
The tool has the following commandline options:
* **-c/--control**: This argument specifies the COM port to be used to configure the mmWave device.
* **-d/--data**: This argument specifies the COM port where we should listen for the data.
* **-f/--file**: This argument specifies the filename of the exported file which contains all the data received.

# mmWave Radar Data replayer

The data replayer application is designed to play the data stored by the data saver (stored in a `.pkl`) file. This uses
the [Frame.py](/Frame.py) file as well to deduce the data being read.

### Commandline Options
The tool has the following options:
* **-f/--file**: This argument specifies the file name of the file to be read