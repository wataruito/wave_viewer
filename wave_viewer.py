'''
wave-viewer.py
'''
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from PyQt5 import QtCore
import hdf5storage


class WaveViewer:
    '''
    WaveViewer
    '''

    def __init__(self, mat_path):
        '''
        '''

        self.mat_path = mat_path
        self.x_width = 3195
        self.x_cur = 0
        self.hmin, self.hmax = 0.0, 8192000.0

        self.spec_data = []
        self.spec_timestamps = []
        self.freq_min, self.freq_max = 0.0, 0.0
        self.fig = []
        self.ax_2d = []

    def wave_viewer(self):
        '''
        wave_viewer()
        '''
        # read spectrogram
        spec = hdf5storage.loadmat(self.mat_path)
        self.spec_data = np.squeeze(spec['powspctrm'][0, :, :])
        self.spec_timestamps = np.squeeze(spec['time'])
        spec_freq = np.squeeze(spec['freq'])

        # create y tick labels
        spec_y = np.arange(0, 201, 25)
        spec_y_value = spec_freq[spec_y].astype(int)

        # compute extent
        xmin = self.x_cur
        xmax = xmin + self.x_width - 1
        extent = [self.spec_timestamps[xmin],
                  self.spec_timestamps[xmax], 0, 200]

        # create window
        mpl.rcParams['toolbar'] = 'None'  # need to put here to hide toolbar
        self.fig = plt.figure()
        self.fig.set_size_inches(10, 2)
        self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = False
        self.fig.canvas.window().statusBar().setVisible(False)

        # move window position and remove title bar
        mngr = plt.get_current_fig_manager()
        geom = mngr.window.geometry()
        _, _, x_len, y_len = geom.getRect()
        mngr.window.setGeometry(0, 100, x_len, y_len)
        mngr.window.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # create subplot
        ax_plot = plt.subplot()
        plt.subplots_adjust(left=0.05, bottom=0, right=1,
                            top=1, wspace=0, hspace=0)

        # show 2D image
        self.ax_2d = ax_plot.imshow(self.spec_data[:, xmin:xmax], extent=extent, cmap=plt.cm.jet,
                                    origin='lower',
                                    aspect='auto')
        # plt.colorbar(im)
        self.ax_2d.set_clim(self.hmin, self.hmax)
        ax_plot.set_yticks(spec_y)
        ax_plot.set_yticklabels(spec_y_value)

        plt.show()

    def press(self, event):
        '''
        press
        '''

        # print('press', event.key)
        sys.stdout.flush()

        # shift = int((self.xmax - self.xmin)/16)
        shift = int(self.x_width/16)
        # hmin, hmax = self.ax_2d.get_clim()

        if event.key == 'down':
            self.x_width = self.x_width * 2
        if event.key == 'up':
            self.x_width = int(self.x_width / 2)
        if event.key == 'left':
            self.x_cur = self.x_cur + shift
            if self.x_cur + self.x_width - 1 > self.spec_timestamps.size - 1:
                self.x_cur = self.spec_timestamps.size - 1 - self.x_width + 1
        if event.key == 'right':
            self.x_cur = self.x_cur - shift
            if self.x_cur < 0:
                self.x_cur = 0
        if event.key == 'h':
            self.hmax = self.hmax / 2
        if event.key == 'c':
            self.hmax = self.hmax * 2
        if event.key == 'e':
            pass

        xmin = self.x_cur
        xmax = xmin + self.x_width - 1
        extent = [self.spec_timestamps[xmin],
                  self.spec_timestamps[xmax], 0, 200]

        print('press', event.key, ': ', xmin, xmax, self.hmax)
        # ax2.set_xlim(xmin, xmax)
        self.ax_2d.set_data(self.spec_data[:, xmin:xmax])
        self.ax_2d.set_clim(self.hmin, self.hmax)
        self.ax_2d.set_extent(extent)
        self.fig.canvas.draw()


if __name__ == '__main__':
    input_path = r'specg.mat'

    win1 = WaveViewer(input_path)
    win1.wave_viewer()
