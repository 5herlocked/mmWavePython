"""
Currently Borrowed from
https://forum.digikey.com/t/getting-started-with-the-ti-awr1642-mmwave-sensor/13445

Using this to brute force save all data from the UART ports
"""
import pickle
import signal
import struct
import time

from datetime import datetime
from queue import PriorityQueue
# Use the correct frame format for the firmware

import numpy as np

from Frame import Frame, ShortRangeRadarFrameHeader, FrameError
from SerialInterface import SerialInterface


class DualPriorityQueue(PriorityQueue):
    def __init__(self, maxPQ=False):
        PriorityQueue.__init__(self)
        self.reverse = -1 if maxPQ else 1

    def put(self, priority, data):
        PriorityQueue.put(self, (self.reverse * priority, data))

    def get(self, *args, **kwargs):
        priority, data = PriorityQueue.get(self, *args, **kwargs)
        return self.reverse * priority, data


def save_data():
    global frames, file_name
    print("Saving data...")
    with open(file_name, 'wb') as file:
        pickle.dump(frames, file)

    print("Verifying data...")
    with open(file_name, 'rb') as file:
        test_frame = pickle.load(file)

        assert frames == test_frame


def kill_all():
    print("Shutting down...")
    interface.send_item(interface.control_tx_queue, 'sensorStop\n')
    time.sleep(2)
    interface.stop()


def interrupt_handler(sig, frame):
    # Sig Int is called causing everything to shut down
    global kill
    kill = True
    kill_all()
    try:
        save_data()
    except Exception as e:
        print(e)


def get_priority(obj):
    # y is away from the chip
    # doppler returns the speed wrt the chip approaching the module
    # use y = 1/x to define danger of object as it approaches user.

    # reduce priority if obj.speed is +ve (away from radar)
    return (1/obj.x) + (1/obj.y) + (1/obj.z) + (-1 * obj.speed)


def announce(most_pressing):
    # abs_x = abs(most_pressing.x)
    # abs_y = abs(most_pressing.y)
    # abs_z = abs(most_pressing.z)

    distance = "really close" if most_pressing.y <= 1 else "close"
    orientation = "left" if most_pressing.x < 0 else "right"

    print("There is an object " + distance + " to your " + orientation)
    pass


def process_frame(plot_queue=None):
    # Open serial interface to the device
    # Specify which frame/header structure to search for
    global interface, frames, kill

    interface.start()

    with open(profile_file) as f:
        print("Sending Configuration...")
        for line in f.readlines():
            if line.startswith('%'):
                # ignore comments
                continue
            else:
                print(line)
                interface.send_item(interface.control_tx_queue, line)

    while not kill:
        serial_frame = interface.recv_item(interface.data_rx_queue)
        if serial_frame:
            try:
                frame = Frame(serial_frame, frame_type=interface.frame_type)
                frames.append(frame)

                if plot_queue is not None:
                    result = dict()

                    for tlv in frame.tlvs:
                        objs = tlv.objects

                        if tlv.name == 'DETECTED_POINTS':
                            tuples = [(float(obj.x), float(obj.y), float(obj.z)) for obj in objs]
                            coords = np.array(tuples)

                            obj_priorities = DualPriorityQueue(True)
                            for obj in objs:
                                obj_priority = get_priority(obj)
                                obj_priorities.put(obj_priority, obj)

                            # If there are objects moving towards the radar chip
                            # with a speed less than -x m/s

                            most_pressing = obj_priorities.get()
                            announce(most_pressing)
                            # for obj in objs:
                            #     #  counteract this when we have IMU data: IMU detected vel - doppler vel
                            #
                            #       if obj.speed <= -1:
                            #         # announce the object
                            #         print("There is an object moving towards you with speed: " + obj.speed)

                            result['DETECTED_POINTS'] = coords

                    plot_queue.put(result)

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
    parser.add_argument('--control_port', help='COM port for configuration, control')
    parser.add_argument('--data_port', help='COM port for radar data transfer')
    parser.add_argument('--output_name', help='Name of the output file')
    parser.add_argument('--vis', help='Start Visualization', action='store_true')
    parser.add_argument('--prof', help='Radar Chirp profile to use')
    args = parser.parse_args()
    # Program Globals
    interface = SerialInterface(args.control_port, args.data_port, frame_type=ShortRangeRadarFrameHeader)
    frames = list()

    if args.prof is not None:
        profile_file = args.prof
    else:
        profile_file = 'profile.cfg'

    if args.output_name is not None:
        file_name = args.output_name + ".pkl"
    else:
        file_name = datetime.now().strftime('%Y_%m_%d-%H-%M-%S') + ".pkl"

    signal.signal(signal.SIGINT, interrupt_handler)
    kill = False
    process_frame()
