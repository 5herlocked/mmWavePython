"""
Currently Borrowed from
https://forum.digikey.com/t/getting-started-with-the-ti-awr1642-mmwave-sensor/13445

Using this to brute force save all data from the UART ports
"""
import struct
import time
from multiprocessing import Queue
from threading import Thread

import numpy as np

# Use the correct frame format for the firmware
from frame import Frame, ShortRangeRadarFrameHeader, FrameError
from serial_interface import SerialInterface

# The SRR firmware is configured for ~20m range with 120 degree viewing angle, about half range should be fine
radar_bounds = (-10, 10, -1, 10)


def generate_new_destination():
    dist = 0
    new_x = 0
    new_y = 0
    while dist < 2:
        new_x = np.random.randint(radar_bounds[0], radar_bounds[1], dtype=np.int8)
        new_y = np.random.randint(0, radar_bounds[3], dtype=np.int8)

        dist = np.sqrt(np.power(new_x, 2) + np.power(new_y, 2))

    return new_x, new_y


def randomize_destination(last_time, period, serial_inst):
    now = time.time()
    if now - last_time > period:
        x, y = generate_new_destination()
        # send_destination(serial_inst, x, y)
        return now
    else:
        return last_time


def process_frame(serial_inst, plot_queue):
    # Get a frame from the data queue and parse
    last_dest_update = 0
    while serial_inst.uarts_enable:
        # Update to a new random destination every 15 seconds
        last_dest_update = randomize_destination(last_dest_update, 15, serial_inst)

        serial_frame = serial_inst.recv_item(serial_inst.data_rx_queue)
        if serial_frame:
            try:
                frame = Frame(serial_frame, frame_type=serial_inst.frame_type)
                results = dict()

                # Frames that don't contain the parking assist data only have 1-2 points
                # Plotting them makes the graph run choppily so just ignore them
                if 'PARKING_ASSIST' in [tlv.name for tlv in frame.tlvs]:
                    # There can be at most one of each type of TLV in the frame
                    for tlv in frame.tlvs:
                        objs = tlv.objects

                        if tlv.name == 'DETECTED_POINTS':
                            tuples = [(float(obj.x), float(obj.y)) for obj in objs]
                            coords = np.array(tuples) / 2 ** tlv.descriptor.xyzQFormat
                            results['DETECTED_POINTS'] = coords

                        elif tlv.name == 'CLUSTERING_RESULTS':
                            tuples = [(float(obj.xCenter), float(obj.xSize),
                                       float(obj.yCenter), float(obj.ySize)) for obj in objs]
                            data = np.array(tuples) / 2 ** tlv.descriptor.xyzQFormat
                            data = np.around(data, 3)
                            results['CLUSTERING_RESULTS'] = data

                        elif tlv.name == 'BEST_PATH':
                            tuples = [(obj.x, obj.y) for obj in objs]
                            # For plotting, offset path by 0.5 so it plots the points in the center of each 1m block
                            path = np.array(tuples) + 0.5
                            if path.size == 0:
                                results['BEST_PATH'] = np.array([[0, 0]])
                            else:
                                results['BEST_PATH'] = path

                    plot_queue.put(results)
            except (KeyError, struct.error, IndexError, FrameError, OverflowError) as e:
                # Some data got in the wrong place, just skip the frame
                print('Exception occured: ', e)
                print("Skipping frame due to error...")

        # Sleep to allow other threads to run
        time.sleep(0.001)


def run_demo(control_port, data_port, reconfig=False):
    # Open serial interface to the device
    # Specify which frame/header structure to search for
    interface = SerialInterface(control_port, data_port, frame_type=ShortRangeRadarFrameHeader)
    interface.start()

    # Write configs to device and start the sensor
    if reconfig:
        print("Sending configuration command...")
        interface.send_item(interface.control_tx_queue, 'advFrameCfg\n')
        time.sleep(3)

        print("Starting sensor...")
        interface.send_item(interface.control_tx_queue, 'sensorStart\n')

    # Create queues that will be used to transfer data between processes
    radar2plot_queue = Queue()

    # Create a thread to parse the frames
    # Sends data to both the plot and the robot
    processing_thread = Thread(target=process_frame, args=(interface, radar2plot_queue,))
    processing_thread.start()

    # Plot instance
    # Receives data from the processing and robot threads
    # my_plot = NavPlot(radar_bounds, radar2plot_queue)
    # my_plot.show()

    # When the plot is closed, stop all the threads and safely end the program
    print("Shutting down...")

    interface.send_item(interface.control_tx_queue, 'sensorStop\n')
    interface.stop()
    processing_thread.join()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run mmWave navigation visualization demo.')
    parser.add_argument('control_port', help='COM port for configuration, control')
    parser.add_argument('data_port', help='COM port for radar data transfer')
    parser.add_argument('--reconfig', help='Send configuration settings to radar', action='store_true')
    args = parser.parse_args()

    run_demo(args.control_port, args.data_port, args.reconfig)
