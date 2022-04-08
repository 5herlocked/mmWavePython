import pickle

from PlotwPlotly import PlotWPlotly
from UartSaver import DualPriorityQueue, get_priority, announce
# Use the correct frame format for the firmware

def run_replay(pickle_file):
    with open(pickle_file, 'rb+') as file:
        frames = pickle.load(file)

    plot = PlotWPlotly(frames)
    plot.show()
    input("Press Enter to quit...")


def simulate_radar_from_file(pickle_file):
    with open(pickle_file, 'rb+') as file:
        frames = pickle.load(file)

        for frame in frames:
            for tlv in frame.tlvs:
                objs = tlv.objects

                if tlv.name == 'DETECTED_POINTS':
                    obj_priorities = DualPriorityQueue(True)

                    for obj in objs:
                        obj_priority = get_priority(obj)
                        obj_priorities.put(obj_priority, obj)

                    most_pressing = obj_priorities.get()

                    announce(most_pressing[1])


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run the pickle replayer for mmWave data')
    parser.add_help = True
    parser.add_argument('--file', help='Location of the pickle file')
    parser.add_argument('--sim', help='Simulate frame processing', action='store_true')
    args = parser.parse_args()

    if not args.sim:
        run_replay(args.file)
    else:
        simulate_radar_from_file(args.file)
