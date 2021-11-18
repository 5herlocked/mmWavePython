"""
Currently Borrowed from
https://forum.digikey.com/t/getting-started-with-the-ti-awr1642-mmwave-sensor/13445

Using this to brute force save all data from the UART ports
"""
import signal
import struct
import time
import json
from datetime import datetime

# Use the correct frame format for the firmware
from Frame import Frame, ShortRangeRadarFrameHeader, FrameError
from SerialInterface import SerialInterface


def save_data():
    global frames, file_name
    json.dump(frames, file_name)


def interrupt_handler(sig, frame):
    # Sig Int is called causing everything to shut down
    print("Saving data...")
    save_data()

    print("Shutting down...")
    interface.send_item(interface.control_tx_queue, 'sensorStop\n')
    interface.stop()
    time.sleep(5)


def run():
    # Open serial interface to the device
    # Specify which frame/header structure to search for
    global interface, frames

    signal.signal(signal.SIGINT, interrupt_handler)
    # interface = SerialInterface(control_port, data_port, frame_type=ShortRangeRadarFrameHeader)
    interface.start()

    with open('profile.cfg') as f:
        print("Sending Configuration...")
        for line in f.readlines():
            if line.startswith('%'):
                continue
            else:
                print(line)
                interface.send_item(interface.control_tx_queue, line)

    frames = []
    start_time = datetime.now()
    while interface.uarts_enable:
        serial_frame = interface.recv_item(interface.data_rx_queue)
        if serial_frame:
            try:
                frame = Frame(serial_frame, frame_type=interface.frame_type)

                frames.append(((datetime.now() - start_time), frame))

            except (KeyError, struct.error, IndexError, FrameError, OverflowError) as e:
                # Some data got in the wrong place, just skip the frame
                print('Exception occurred: ', e)
                print("Skipping frame due to error...")

        # Sleep to allow other threads to run
        time.sleep(0.001)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run mmWave record of the data received')
    parser.add_help = True
    parser.add_argument('control_port', help='COM port for configuration, control')
    parser.add_argument('data_port', help='COM port for radar data transfer')
    parser.add_argument('output_name', help='Name of the output file')
    args = parser.parse_args()

    # Program Globals
    interface = SerialInterface(args.control_port, args.data_port, frame_type=ShortRangeRadarFrameHeader)
    frames = list()

    if args.output_name is not None:
        file_name = args.output_name + ".json"
    else:
        file_name = datetime.now().strftime('%Y_%m_%d-%H-%M-%S') + ".json"

    run()
