from multiprocessing import Queue

import numpy as np

from NavPlot import NavPlot


class ReplayPlot(NavPlot):
    def __init__(self, curr_pos=0, frames=None):
        radar_queue = Queue()
        super().__init__(radar_queue)

        self.curr_pos = curr_pos
        self.frames = frames
        self.prev_pos = curr_pos

        self.fig.canvas.mpl_connect('key_press_event', self.key_event)

    def key_event(self, e):
        if e.key == 'right':
            self.prev_pos = self.curr_pos
            self.curr_pos += 1
        elif e.key == 'left':
            self.prev_pos = self.curr_pos
            self.curr_pos -= 1

    def update_plot(self):
        # Keep track of things that have changed for the animation
        modified_artists = []

        frame = self.frames[self.curr_pos]

        result = dict()

        for tlv in frame.tlvs:
            objs = tlv.objects

            if tlv.name == 'DETECTED_POINTS':
                tuples = [(float(obj.x), float(obj.y)) for obj in objs]
                coords = np.array(tuples)
                result['DETECTED_POINTS'] = coords

        if 'DETECTED_POINTS' in result.keys():
            detections = result['DETECTED_POINTS']
            self.obj_scatter.set_offsets(detections[:, 0:2])
            modified_artists.append(self.obj_scatter)

        self.prev_artists = modified_artists

        return modified_artists
