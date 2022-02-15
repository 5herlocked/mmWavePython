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

        self.fig.data[0].visible = True
        self.fig.update_layout(sliders=sliders)

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
