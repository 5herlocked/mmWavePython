# Basically
# This is the idea
# On button 1 press - start data collection (stream camera to file + stream radar to file)
# On button 2 press - stop data collection


# pseudocode
# on launch
#   open serial interface + open camera interface in TWO seperate threads
#   BUT do NOT start recording
# on gpio rising edge:
#   start serial recording
#   in this thread we:  read serial, convert to CSV
#   start camera recording
#   in this thread we: read camera frame, store frame locally

# what we need:
#   Serial Reader class: launch/open_serial() | process_frame() | close_serial()
#           save_frame()
#   Camera Reader class: launch/open_camera() | process_frame() | close_camera()
#           save_frame()


import threading
import SerialReader
import CameraReader

