import pickle

from PlotwPlotly import PlotWPlotly


# Use the correct frame format for the firmware

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
