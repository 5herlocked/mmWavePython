import csv
import struct

from Frame import ShortRangeRadarFrameHeader, Frame, FrameError
from datetime import datetime
from threading import Thread
from multiprocessing import Queue
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

                    for tlv in frame.tlvs:
                        objs = tlv.objects

                        if tlv.name == 'DETECTED_POINTS':
                            self.received_queue.put(objs)

                except(KeyError, struct.error, IndexError, FrameError, OverflowError) as e:
                    print('Exception occurred: ', e)
                    print('Skipping frame')

    def process_storing(self):
        # if running or received queue has stuff in it
        counter = 1
        with open(self.file, 'x+', newline='\n') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(['time', 'frame_number', 'object_number', 'x (m)', 'y(m)', 'z(m)', 'doppler (m/s)'])

            while self.running or not self.received_queue.empty():
                received_objs = self.received_queue.get()
                if received_objs.name == 'DETECTED_POINTS':
                    inner = 1
                    for obj in received_objs:
                        x = obj.x
                        y = obj.y
                        z = obj.z
                        speed = obj.doppler
                        time_instant = datetime.now().isoformat()

                        writer.writerow([time_instant, counter, inner, x, y, z, speed])
                        inner += 1
                    counter += 1

    def send_profile(self, profile_file):
        with open(profile_file) as f:
            for line in f.readlines():
                if line.startswith('%'):
                    continue
                else:
                    self.interface.send_item(self.interface.control_tx_queue, line)

    def start(self):
        self.running = True
        self.receiving_process.start()

    def stop(self):
        self.running = False
        self.receiving_process.join()
