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

    def __init__(self, mat_path, d_type):
        '''
        '''

        self.mat_path = mat_path
        self.d_type = d_type

        self.x_width = 3195
        self.x_cur = 0
        self.hmin, self.hmax = 0.0, 8192000.0

        self.wave_data = []
        self.wave_timestamps = []

        self.spec_data = []
        self.spec_timestamps = []
        self.freq_min, self.freq_max = 0.0, 0.0

        self.fig = []
        self.ax_plot = []
        self.ax_1d = []
        self.ax_2d = []

    def wave_viewer(self):
        '''
        wave_viewer()
        '''

        if self.d_type == 'spec':
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
            # need to put here to hide toolbar
            mpl.rcParams['toolbar'] = 'None'
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
            # adjust 2D image
            # plt.colorbar(im)
            self.ax_2d.set_clim(self.hmin, self.hmax)
            ax_plot.set_yticks(spec_y)
            ax_plot.set_yticklabels(spec_y_value)

        else:
            # read wave
            wave = hdf5storage.loadmat(self.mat_path)
            self.wave_data = np.squeeze(wave['data'])[:, 0]
            self.wave_timestamps = np.squeeze(wave['timestamps'])

            # compute extent
            xmin = self.x_cur
            xmax = xmin + self.x_width - 1
            xmin *= 10
            xmax *= 10
            # extent = [self.wave_timestamps[xmin], self.wave_timestamps[xmax]]

            # create window
            # need to put here to hide toolbar
            mpl.rcParams['toolbar'] = 'None'
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
            self.ax_plot = plt.subplot()
            plt.subplots_adjust(left=0.05, bottom=0, right=1,
                                top=1, wspace=0, hspace=0)

            # plot wave
            self.ax_1d, = self.ax_plot.plot(
                self.wave_timestamps[xmin:xmax], self.wave_data[xmin:xmax], linewidth=0.5)
            # ax.set_xlim(2000, 2010)

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

        if self.d_type == 'spec':
            xmax_lim = self.spec_timestamps.size
            # timestamps = self.spec_timestamps
        else:
            xmax_lim = int(self.wave_timestamps.size / 10) + 1
            # timestamps = self.wave_timestamps

        if event.key == 'right':
            self.x_cur = self.x_cur + shift
            if self.x_cur + self.x_width - 1 > xmax_lim - 1:
                self.x_cur = xmax_lim - 1 - self.x_width + 1
        if event.key == 'left':
            self.x_cur = self.x_cur - shift
            if self.x_cur < 0:
                self.x_cur = 0
        if event.key == 'down':
            self.x_width = self.x_width * 2
        if event.key == 'up':
            self.x_width = int(self.x_width / 2)
        if event.key == 'h':
            self.hmax = self.hmax / 2
        if event.key == 'c':
            self.hmax = self.hmax * 2
        if event.key == 'e':
            pass

        xmin = self.x_cur
        xmax = xmin + self.x_width - 1

        if self.d_type == 'spec':
            extent = [self.spec_timestamps[xmin],
                      self.spec_timestamps[xmax], 0, 200]

            print('press', event.key, ': ', xmin, xmax, self.hmax)
            # ax2.set_xlim(xmin, xmax)
            self.ax_2d.set_data(self.spec_data[:, xmin:xmax])
            self.ax_2d.set_clim(self.hmin, self.hmax)
            self.ax_2d.set_extent(extent)
        else:
            xmin *= 10
            xmax *= 10

            print('press', event.key, ': ', xmin, xmax)
            # self.ax_1d.set_xdata(self.wave_timestamps[xmin:xmax])
            # self.ax_1d.set_ydata(self.wave_data[xmin:xmax])
            self.ax_1d.set_data(
                self.wave_timestamps[xmin:xmax], self.wave_data[xmin:xmax])
            self.ax_plot.relim()
            self.ax_plot.autoscale_view(True, True, True)

        self.fig.canvas.draw()


if __name__ == '__main__':
    # input_path = r'specg.mat'
    # input_d_type = 'spec'
    input_path = r'gamma1_flat.mat'
    input_d_type = 'gamma'

    win1 = WaveViewer(input_path, input_d_type)
    win1.wave_viewer()
