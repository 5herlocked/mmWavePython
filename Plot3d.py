import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from PlotHelpers import *


class Plot3D:
    def __init__(self, radar_queue_in=None):
        fig = plt.figure(figsize=(6, 6))
        ax = plt.subplot(1, 1, 1, projection='3d')  # rows, cols, idx

        ax.view_init(azim=-45, elev=15)

        move_figure(fig, (0 + 45 * 2, 0 + 45 * 2))

        fig.canvas.manager.set_window_title('...')

        ax.set_title('CFAR Detection'.format(), fontsize=10)

        ax.set_xlabel('x [m]')
        ax.set_ylabel('y [m]')
        ax.set_zlabel('z [m]')

        ax.set_xlim3d((-5, 5))
        ax.set_ylim3d((0, 5))
        ax.set_zlim3d((-5, 5))

        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False

        ax.xaxis._axinfo['grid']['linestyle'] = ':'
        ax.yaxis._axinfo['grid']['linestyle'] = ':'
        ax.zaxis._axinfo['grid']['linestyle'] = ':'

        fig.tight_layout(pad=1)

        for child in ax.get_children():
            if isinstance(child, art3d.Path3DCollection):
                child.remove()

        from itertools import product, combinations  # a small cube (origin)
        r = [-0.075, +0.075]
        for s, e in combinations(np.array(list(product(r, r, r))), 2):
            if np.sum(np.abs(s - e)) == r[1] - r[0]:
                ax.plot3D(*zip(s, e), color="black", linewidth=0.5)

        set_aspect_equal_3d(ax)

        mpl.colors._colors_full_map.cache.clear()  # avoid memory leak by clearing the cache
        self.fig = fig
        self.ax = ax
        self.radar_queue = radar_queue_in

        self.obj_scatter = self.ax.scatter(xs=[], ys=[], zs=[], marker='.', cmap='jet')

        self.prev_artists = []
        self.ani = FuncAnimation(self.fig, self.update, interval=16, blit=False)

    def update(self, _frame):
        modified_artists = []

        modified_artists.extend(self.update_plot())

        return modified_artists

    def update_plot(self):
        radar_data = self.radar_queue.get()

        xm, ym, zm = self.ax.get_xlim3d(), self.ax.get_ylim3d(), self.ax.get_zlim3d()

        modified_artists = []

        if 'DETECTED_POINTS' not in radar_data:
            return self.prev_artists

        detections = radar_data['DETECTED_POINTS']

        self.obj_scatter.set_offsets(detections[:, 0:3])
        print(detections[:, 0:3])

        modified_artists.append(self.obj_scatter)

        # for obj in detections:
        #     x, y, z = obj[0], obj[1], obj[2]
        #
        #     modified_artists.append(obj[0:3])
        #
        #     pt = Point((x, y, z), size=3, marker='.')
        #     modified_artists.append(pt)
        #
        #     az, el = self.ax.azim, self.ax.elev
        #
        #     if abs(az) > 90:
        #         x_ = max(xm)
        #     else:
        #         x_ = min(xm)
        #
        #     if az < 0:
        #         y_ = max(ym)
        #     else:
        #         y_ = min(ym)
        #
        #     if el < 0:
        #         z_ = max(zm)
        #     else:
        #         z_ = min(zm)
        #
        #     xz = Point((x, y_, z), color=(0.67, 0.67, 0.67), size=1, marker='.')
        #     modified_artists.append(xz)
        #
        #     yz = Point((x_, y, z), color=(0.67, 0.67, 0.67), size=1, marker='.')
        #     modified_artists.append(yz)
        #
        #     xy = Point((x, y, z_), color=(0.67, 0.67, 0.67), size=1, marker='.')
        #     modified_artists.append(xy)

        return modified_artists

    def show(self):
        plt.show(block=True)