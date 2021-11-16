import numpy as np
import time

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import patches
from matplotlib.collections import PatchCollection

from math import tan, radians


class NavPlot:
    def __init__(self, radar_bounds, radar_queue_in=None):
        matplotlib.rcParams['toolbar'] = 'None'

        # Copy all the bounding data
        self.radar_left_bound = radar_bounds[0]
        self.radar_right_bound = radar_bounds[1]
        self.radar_back_bound = radar_bounds[2]
        self.radar_front_bound = radar_bounds[3]

        # Queues to receive data
        self.radar_queue = radar_queue_in

        # Initialize plots
        self.fig = plt.figure()
        self.radar_ax = self.fig.add_subplot(111)
        self.radar_plot_init()

        # Initialize the actual plot with empty data
        self.obj_scatter = self.radar_ax.scatter([], [], s=60, marker='o')
        self.radar_path_plot, = self.radar_ax.plot([], [], 'go--')

        # Save results from previous update in case there is no new radar data ready, keeps plot smooth
        self.prev_artists = []

        # Set refresh rate to ~60 Hz
        self.ani = FuncAnimation(self.fig, self.update, interval=16, blit=True)

    def radar_plot_init(self):
        self.radar_ax.set_title('Radar Plot')
        self.radar_ax.set_aspect('equal')
        self.radar_ax.set_xlabel('X (m)')
        self.radar_ax.set_ylabel('Y (m)')
        self.radar_ax.set_xlim(self.radar_left_bound, self.radar_right_bound)
        self.radar_ax.set_ylim(self.radar_back_bound, self.radar_front_bound)

        # Invert axes to match current positioning
        # self.radar_ax.invert_yaxis()
        # self.radar_ax.invert_xaxis()
        # self.radar_ax.xaxis.set_label_position('top')
        # self.radar_ax.xaxis.tick_top()

        # Configure grid
        minor_xticks = np.arange(self.radar_left_bound, self.radar_right_bound, 0.5)
        minor_yticks = np.arange(self.radar_back_bound, self.radar_front_bound, 0.5)
        self.radar_ax.set_xticks(minor_xticks, minor=True)
        self.radar_ax.set_yticks(minor_yticks, minor=True)
        self.radar_ax.grid(True, which='both')

        # Draw an section to make the graph look radar-y
        x_size = abs(self.radar_left_bound) + abs(self.radar_right_bound)
        y_size = 2 * abs(self.radar_front_bound)
        arc = patches.Arc((0, 0), x_size, y_size, 0, theta1=30, theta2=150)

        half_rad = self.radar_front_bound / 2
        line_x = half_rad * tan(radians(60))
        left_line = patches.ConnectionPatch((0.5, 0), (-line_x, half_rad), coordsA='data', coordsB='data')
        right_line = patches.ConnectionPatch((0.5, 0), (line_x, half_rad), coordsA='data', coordsB='data')

        self.radar_ax.add_patch(arc)
        self.radar_ax.add_patch(left_line)
        self.radar_ax.add_patch(right_line)

    def update_obstacles(self):
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

                # Create shaded regions to mark blocked areas
                boxes = []
                for pt in detections:
                    xmin = np.floor(pt[0])
                    ymin = np.floor(pt[1])

                    box = patches.Rectangle((xmin, ymin), width=1.0, height=1.0, fill=True)
                    boxes.append(box)

                detect_pc = PatchCollection(boxes, facecolor='r', alpha=0.2)
                self.radar_ax.add_collection(detect_pc)
                modified_artists.append(detect_pc)

            if 'CLUSTERING_RESULTS' in radar_data.keys():
                clusters = radar_data['CLUSTERING_RESULTS']

                for cluster in clusters:
                    xmin = cluster[0] - (cluster[1] / 2)
                    width = cluster[1]
                    ymin = cluster[2] - (cluster[3] / 2)
                    height = cluster[3]
                    rect = patches.Rectangle((xmin, ymin), width=width, height=height, color='#99ff33', fill=False)

                    # Do the rectangles individually to preserve the fill=False flag (does't work with PatchCollection)
                    self.radar_ax.add_patch(rect)
                    modified_artists.append(rect)

            if 'BEST_PATH' in radar_data.keys():
                path = radar_data['BEST_PATH']
                self.radar_path_plot.set_data(path[:, 0], path[:, 1])
                modified_artists.append(self.radar_path_plot)

                # Draw the origin in a different color
                xmin = np.floor(path[0][0])
                ymin = np.floor(path[0][1])
                box = patches.Rectangle((xmin, ymin), width=1.0, height=1.0, fill=False, color='b')
                self.radar_ax.add_patch(box)
                modified_artists.append(box)

                boxes = []
                for pt in path[1:]:
                    xmin = np.floor(pt[0])
                    ymin = np.floor(pt[1])

                    box = patches.Rectangle((xmin, ymin), width=1.0, height=1.0, fill=False)
                    boxes.append(box)

                path_pc = PatchCollection(boxes, facecolors='g', alpha=0.5)
                self.radar_ax.add_collection(path_pc)
                modified_artists.append(path_pc)

        self.prev_artists = modified_artists
        return modified_artists

    def update(self, frame):
        # Keep track of things that have changed for the animation
        modified_artists = []

        # Add any changes from either the obstacle detection or robot movement
        modified_artists.extend(self.update_obstacles())

        return modified_artists

    def show(self):
        plt.tight_layout()
        plt.show()