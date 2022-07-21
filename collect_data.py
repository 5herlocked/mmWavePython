# Basically
# This is the idea
# On button 1 press - start data collection (stream camera to file + stream radar to file)
# On button 2 press - stop data collection


# pseudocode
# on launch
#   open serial interface + open camera interface in TWO separate threads
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
import signal
import time

from SerialReader import SerialReader
from CameraReader import CameraReader


def interrupt_handler(sig, frame):
    global kill
    kill = True
    stop_watching()


def stop_watching():
    camera.stop()
    serial.stop()


def start_watching():
    global kill
    camera.start()
    serial.start()

    while not kill:
        time.sleep(0.5)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run the data collection pipeline')
    parser.add_help = True
    parser.add_argument('--control_port', help='COM port for configuration, control')
    parser.add_argument('--data_port', help='COM port for radar data transfer')
    parser.add_argument('--output_name', help='Name of the output collection of files')
    parser.add_argument('--prof', help='Radar Chirp profile to use')
    args = parser.parse_args()

    kill = False

    signal.signal(signal.SIGINT, interrupt_handler)

    camera = CameraReader(args.output_name + '.mp4')
    serial = SerialReader(args.output_name + '.csv', args.control_port, args.data_port)

    start_watching()
