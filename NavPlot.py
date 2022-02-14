import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class NavPlot:
    def __init__(self, radar_queue_in=None):
        matplotlib.rcParams['toolbar'] = 'None'

        # Queues to receive data
        self.radar_queue = radar_queue_in

        # Initialize plots
        self.fig = plt.figure()
        self.radar_ax = self.fig.add_subplot(111)
        self.radar_plot_init()

        # Initialize the actual plot with empty data
        self.obj_scatter = self.radar_ax.scatter([], [], s=60, marker='o')

        # Save results from previous update in case there is no new radar data ready, keeps plot smooth
        self.prev_artists = []

        # Set refresh rate to ~16 Hz
        self.ani = FuncAnimation(self.fig, self.update, interval=16, blit=True)

    def radar_plot_init(self):
        self.radar_ax.set_title('Radar Plot')
        self.radar_ax.set_aspect('auto')
        self.radar_ax.set_xlabel('X (m)')
        self.radar_ax.set_ylabel('Y (m)')
        self.radar_ax.set_xlim(-10, 10)
        self.radar_ax.set_ylim(0, 10)

    def update_plot(self):
        # Keep track of things that have changed for the animation
        modified_artists = []

        # Obstacle detection data
        radar_data = self.radar_queue.get()
        if len(radar_data) == 0:
            # Keep data from last frame so plot doesn't get choppy
            modified_artists = self.prev_artists
        else:
            # Process each TLV type
            if 'DETECTED_POINTS' in radar_data.keys():
                detections = radar_data['DETECTED_POINTS']
                self.obj_scatter.set_offsets(detections[:, 0:2])
                modified_artists.append(self.obj_scatter)

        self.prev_artists = modified_artists
        return modified_artists

    def update(self, frame):
        # Keep track of things that have changed for the animation
        modified_artists = []

        # Add any changes from either the obstacle detection or robot movement
        modified_artists.extend(self.update_plot())

        return modified_artists

    def show(self):
        plt.tight_layout()
        plt.show(block=True)

