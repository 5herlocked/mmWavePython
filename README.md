# mmWave Radar data saver

The data saver application is specifically designed to export the data packets returned 
by the [Out-of-Box Demo](https://dev.ti.com/tirex/explore/node?devtools=IWR6843ISK&node=ADSocWGX8FJCytCWREvHzw__VLyFKFf__LATEST)
for the Ti IWR-6843-ISK module. The [frame.py](./frame.py) file can be manipulated to fit your specific usecase.
It is recommended that you change the frame.py file whenever you modify the data return patterns of the mmWave radar.

### Commandline Options
The tool has the following commandline options:
* **-c/--control**: This argument specifies the COM port to be used to configure the mmWave device.
* **-d/--data**: This argument specifies the COM port where we should listen for the data.
* **-f/--file**: This argument specifies the filename of the exported file which contains all the data received.


### Possible use cases
We at MORSEStudio are going to use this primarily to store all of the data generated as part of our initial exposure to
mmWave radar technology.