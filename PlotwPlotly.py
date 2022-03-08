import plotly.graph_objects as go


class PlotWPlotly:
    def __init__(self, frames):
        self.fig = go.Figure()
        self.get_traces(frames)
        steps = []
        for i in range(len(self.fig.data)):
            step = dict(
                method="update",
                args=[{"visible": [False] * len(self.fig.data)},
                      {"title": "Frame Number: " + str(i)}],
            )
            step["args"][0]["visible"][i] = True
            steps.append(step)

        sliders = [dict(
            active=0,
            currentvalue={"prefix": "Frame: "},
            pad={"t": 50},
            steps=steps
        )]
        scene = dict(
            xaxis = dict(range=[-10, 10]),
            yaxis = dict(range=[-10, 10]),
            zaxis = dict(range=[-2, 10])
        )

        camera = dict(
            center=dict(x=10, y=10, z=10),
            eye=dict(x=0, y=0, z=0),
        )

        self.fig.data[0].visible = True
        self.fig.update_layout(scene=scene,
                               scene_camera=camera, sliders=sliders)

    def get_traces(self, frames):
        for frame, i in zip(frames, range(1, len(frames))):
            for tlv in frame.tlvs:
                objs = tlv.objects
                if tlv.name == 'DETECTED_POINTS':
                    self.fig.add_trace(
                        go.Scatter3d(
                            visible=False,
                            name='frame = ' + str(i),
                            x=[float(obj.x) for obj in objs],
                            y=[float(obj.y) for obj in objs],
                            z=[float(obj.z) for obj in objs],
                            mode='markers',
                            uirevision='0',
                        )
                    )

    def show(self):
        self.fig.show()
