# Serial Reader Threaded class
#
#
#
import struct
from multiprocessing import Queue
from threading import Thread
from Frame import ShortRangeRadarFrameHeader, Frame, FrameError
from SerialInterface import SerialInterface


class SerialReader:
    def __init__(self, file, control, data):
        self.interface = SerialInterface(control, data, frame_type=ShortRangeRadarFrameHeader)
        self.file = file

        self.running = False

        self.received_queue = Queue()

        self.receiving_process = Thread(target=self.process_receiving)
        self.storing_process = Thread(target=self.process_storing)

    def process_receiving(self):
        while self.running:
            frame = self.interface.recv_item(self.interface.data_rx_queue)

            if frame:
                try:
                    frame = Frame(frame, frame_type=self.interface.frame_type)
                    pass
                except(KeyError, struct.error, IndexError, FrameError, OverflowError) as e:
                    print('Exception occurred: ', e)
                    print('Skipping frame')

    def process_storing(self):
        while self.running:
            pass

    def send_profile(self, profile_file):
        with open(profile_file) as f:
            for line in f.readlines():
                if line.startswith('%'):
                    continue
                else:
                    self.interface.send_item(self.interface.control_tx_queue, line)

    def stop(self):
        self.running = False

        self.receiving_process.join()
