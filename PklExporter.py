import datetime
import pickle
import csv


def export_data(pickle_file, csv_file):
    with open(pickle_file, 'rb+') as file:
        frames = pickle.load(file)

    with open(csv_file, 'x+', newline='\n') as csvFile:
        writer = csv.writer(csvFile)
        # write the header
        writer.writerow(['time_instant', 'frame_number', 'object_number', 'x', 'y', 'z'])

        counter = 1
        for frame in frames:
            for tlv in frame.tlvs:
                objs = tlv.objects

                if tlv.name == 'DETECTED_POINTS':
                    inner = 1
                    for obj in objs:
                        x = obj.x
                        y = obj.y
                        z = obj.z
                        # write each row
                        if frame.time is None:
                            frame.time = datetime.datetime.now()

                        writer.writerow([frame.time, counter, inner, x, y, z])
                        inner += 1
            counter += 1


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run the pkl to csv exporter')
    parser.add_help = True
    parser.add_argument('--file', help='Pickle File name to export')

    args = parser.parse_args()

    output_filename = args.file.split('.')
    if len(output_filename[0]) == 0:
        output_filename = output_filename[1]
    else:
        output_filename = output_filename[0]

    print(output_filename)
    output_filename += '.csv'

    export_data(args.file, output_filename)