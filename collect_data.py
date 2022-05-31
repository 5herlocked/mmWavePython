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


from threading import Thread
import SerialReader
import CameraReader


def open_files():
    pass


def watch_camera():
    with open('' + args.output_name + '.mp4', mode='wb+') as vid:
        # Create an instance of CameraReader and pass the file to it
        pass

    pass


def watch_serial():
    with open('' + args.output_name + '.csv', mode='w+') as csv:
        # Create an instance of SerialReader and pass the file to it
        pass
    pass


async def watch():
    camera_thread = Thread(target=watch_camera)
    serial_thread = Thread(target=watch_serial)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run the data collection pipeline')
    parser.add_help = True
    parser.add_argument('--control_port', help='COM port for configuration, control')
    parser.add_argument('--data_port', help='COM port for radar data transfer')
    parser.add_argument('--output_name', help='Name of the output collection of files')
    parser.add_argument('--prof', help='Radar Chirp profile to use')
    args = parser.parse_args()

    await watch()
