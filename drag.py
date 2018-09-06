import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
import matplotlib

class DraggablePoint:

    lock = None

    def __init__(self, parent, dominant, x=10, y=10, size=10, xc=1, yc=1):
        """Creates a draggable Point on a matplotlib canvas"""
        matplotlib.matplotlib_fname()
        # The FigureCanvas
        self.parent = parent
        # The Point
        self.point = patches.Ellipse((x, y), size*xc, size*yc, fc='g', alpha=0.5, edgecolor='g')
        #Coordinates of the point
        self.x = x
        self.y = y
        self.x_offset = 0
        self.y_offset = 0
        self.dy = 0
        self.dx = 0
        self.x_offset_factor = 0
        self.y_offset_factor = 0
        self.x_scaling = self.x * self.x_offset_factor
        self.y_scaling = self.y * self.y_offset_factor
        self.dy = self.y_offset + self.y_scaling
        self.dx = self.x_offset + self.x_scaling
        # self.otherX = ox
        # self.otherY = oy
        # Adds the point to the Plot
        parent.fig.axes[0].add_patch(self.point)
        # Used in the on_press() function
        self.press = None
        self.background = None
        # initiate the mpl_connects
        self.connect()
        # The Other DraggablePoint, with whom the line shall connect with.
        self.partner = None
        # The Line2D
        self.line = None
        self.dominant = dominant


    def drawline(self):
        for pair in self.parent.point_pairs:
            if self in pair:
                if self == pair[1]:
                    line_x = [pair[0].x + pair[0].dx, self.x+self.dx]
                    line_y = [pair[0].y + pair[0].dy, self.y+self.dy]
                    self.line = Line2D(line_x, line_y, color='r', alpha=0.5)
                    self.parent.fig.axes[0].add_line(self.line)
                else:
                    line_x = [pair[1].x + pair[1].dx, self.x + self.dx]
                    line_y = [pair[1].y + pair[1].dy, self.y + self.dy]
                    self.line = Line2D(line_x, line_y, color='r', alpha=0.5)
                    self.parent.fig.axes[0].add_line(self.line)

        for pair in self.parent.point_pairs:
            self.point.axes.draw_artist(pair[1].line)

    def connect(self):

        'connect to all the events we need'
        # print("LOG.INFO: DraggablePoint.connect")
        self.cidpress = self.point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)


    def on_press(self, event):
        '''Initiates when a Point is clicked on'''
        if event.inaxes != self.point.axes: return
        if DraggablePoint.lock is not None: return
        contains, attrd = self.point.contains(event)
        if not contains: return
        self.press = (self.point.center), event.xdata, event.ydata
        DraggablePoint.lock = self


        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.point.figure.canvas
        axes = self.point.axes
        self.point.set_animated(True)
        for pair in self.parent.point_pairs:
            if self == pair[1]:
                self.line.set_animated(True)
            elif self == pair[0]:
                self.partner.line.set_animated(True)


        canvas.draw()
        self.background = canvas.copy_from_bbox(self.point.axes.bbox)

        # now redraw just the rectangle
        axes.draw_artist(self.point)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)

        while (self.parent.fig.axes[0].lines != []): self.parent.fig.axes[0].lines.pop()


    def on_motion(self, event):

        # print("LOG.INFO: DraggablePoint.on_motion")
        if DraggablePoint.lock is not self:
            return
        if event.inaxes != self.point.axes: return
        # print("LOG.INFO: DraggablePoint.on_motion.after_lock")
        # self.parent.updateFigure()
        self.point.center, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.point.center = (self.point.center[0]+dx, self.point.center[1]+dy)

        #Update the scaling of the offset
        self.x_scaling = self.x * self.x_offset_factor
        self.y_scaling = self.y * self.y_offset_factor
        self.dy = self.y_offset + self.y_scaling
        self.dx = self.x_offset + self.x_scaling

        canvas = self.point.figure.canvas
        axes = self.point.axes
        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current rectangle
        axes.draw_artist(self.point)

        for pair in self.parent.point_pairs:
            if self in pair:
                axes.draw_artist(pair[1].line)
            if self == pair[1]:
                self.x_scaling = self.x * self.x_offset_factor
                self.y_scaling = self.y * self.y_offset_factor
                self.dy = self.y_offset + self.y_scaling
                self.dx = self.x_offset + self.x_scaling


        self.x = self.point.center[0]
        self.y = self.point.center[1]

        for pair in self.parent.point_pairs:
            if self == pair[1]:
                line_x = [pair[0].x + pair[0].dx, self.x+self.dx]
                line_y = [pair[0].y + pair[0].dy, self.y+self.dy]
                self.line.set_data(line_x, line_y)
            elif self == pair[0]:
                line_x = [pair[1].x + pair[1].dx, self.x+self.dx]
                line_y = [pair[1].y + pair[1].dy, self.y+self.dy]
                pair[1].line.set_data(line_x, line_y)

        # blit just the redrawn area
        canvas.blit(axes.bbox)
        # print(self.line)        


    def on_release(self, event):

        # print("LOG.INFO: DraggablePoint.on_release")
        'on release we reset the press data'
        if DraggablePoint.lock is not self:
            return

        # print("LOG.INFO: DraggablePoint.on_release.after_lock")
        self.press = None
        DraggablePoint.lock = None

        # turn off the rect animation property and reset the background
        self.point.set_animated(False)
        axes = self.point.axes

        for pair in self.parent.point_pairs:
            if self in pair:
                if pair[1] == self:
                    self.line.set_animated(False)
                else:
                    pair[1].line.set_animated(False)

        print(self.x_scaling, self.y_scaling)

        self.background = None

        # redraw the full figure
        self.point.figure.canvas.draw()

        self.x = self.point.center[0]
        self.y = self.point.center[1]

        for pair in self.parent.point_pairs:
            axes.draw_artist(pair[1].line)
        print(self.line.__str__() + "RELEASE")

        for pair in self.parent.point_pairs:
            if self in pair:
                if pair[1] == self:
                    axes.draw_artist(self.line)
                else:
                    axes.draw_artist(pair[1].line)

        self.parent.plot()
        self.drawline()
        for pair in self.parent.point_pairs:
            #print(pair[0].x, pair[0].y, pair[1].x, pair[1].y)
            self.parent.setIntercept(pair[0].x, pair[0].y, pair[1].x, pair[1].y)
        self.parent.updateQ()


    def disconnect(self):

        'disconnect all the stored connection ids'

        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)

    def setLine(self, line):
        self.line = line


