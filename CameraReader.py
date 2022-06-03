import cv2 as cv

from threading import Thread
from multiprocessing import Queue


class CameraReader:
    def __init__(self, video_source, output_file):
        self.running = False

        self.camera = cv.VideoCapture(video_source)
        if not self.camera.isOpened():
            print("Cannot open Camera")
            exit()

        fourcc = cv.VideoWriter_fourcc(*'XVID')

        # write to output file with the fourcc codec and 640x480@60fps
        self.writer = cv.VideoWriter(output_file, fourcc, 60.0, (640, 480))

        self.frame_queue = Queue()

        self.recording_thread = Thread(target=self.record)
        self.storing_thread = Thread(target=self.store)
        pass

    def record(self):
        while self.running:
            ret, frame = self.camera.read()
            if not ret:
                print("Dropped frame")

            self.frame_queue.put(frame)

    def store(self):
        while self.running or not self.frame_queue.empty():
            self.writer.write(self.frame_queue.get())

    def start(self):
        self.running = True

        self.storing_thread.start()
        self.recording_thread.start()
        pass

    def stop(self):
        self.running = False

        self.recording_thread.join()
        self.storing_thread.join()
        pass
