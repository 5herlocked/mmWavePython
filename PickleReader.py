"""
Currently Borrowed from
https://forum.digikey.com/t/getting-started-with-the-ti-awr1642-mmwave-sensor/13445

Using this to brute force save all data from the UART ports
"""
import pickle
import time

import numpy as np

from PlotwPlotly import PlotWPlotly
from ReplayPlot import ReplayPlot


# Use the correct frame format for the firmware


# def load_data(pickle_file, plot_queue=None):
#     with open(pickle_file, 'rb+') as file:
#         frames = pickle.load(file)
#
#     for frame in frames:
#         result = dict()
#
#         for tlv in frame.tlvs:
#             objs = tlv.objects
#
#             if tlv.name == 'DETECTED_POINTS':
#                 tuples = [(float(obj.x), float(obj.y), float(obj.z)) for obj in objs]
#                 coords = np.array(tuples)
#                 result['DETECTED_POINTS'] = coords
#
#             plot_queue.put(result)
#         time.sleep(0.1)


def run_replay(pickle_file):
    with open(pickle_file, 'rb+') as file:
        frames = pickle.load(file)

    plot = PlotWPlotly(frames)
    plot.show()
    input("Press Enter to quit...")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run the pickle replayer for mmWave data')
    parser.add_help = True
    parser.add_argument('--file', help='Location of the pickle file')
    args = parser.parse_args()

    run_replay(args.file)
