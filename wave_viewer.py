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
        self.x_width = 100
        self.x_cur = 0

        self.spec_data = []
        self.fig = []
        self.ax_2d = []

    def wave_viewer(self):
        '''
        wave_viewer()
        '''

        hmin, hmax = 0, 1000
        xmin = self.x_cur
        xmax = xmin + self.x_width - 1

        # read spectrogram
        spec = hdf5storage.loadmat(self.mat_path)
        self.spec_data = np.squeeze(spec['powspctrm'][0, :, :])
        # spec_timestamps = np.squeeze(spec['time'])
        # spec_freq = np.squeeze(spec['freq'])

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
        self.ax_2d = ax_plot.imshow(self.spec_data[:, xmin:xmax], cmap=plt.cm.jet,
                                    aspect='auto')
        # plt.colorbar(im)
        self.ax_2d.set_clim(hmin, hmax)

        plt.show()

    def press(self, event):
        '''
        press
        '''

        print('press', event.key)
        sys.stdout.flush()

        # shift = int((self.xmax - self.xmin)/16)
        shift = int(self.x_width/16)
        hmin, hmax = self.ax_2d.get_clim()

        if event.key == 'down':
            self.x_width = self.x_width * 2
        if event.key == 'up':
            self.x_width = int(self.x_width / 2)
        if event.key == 'left':
            self.x_cur = self.x_cur + shift
        if event.key == 'right':
            self.x_cur = self.x_cur - shift
        if event.key == 'h':
            hmax = hmax / 2
        if event.key == 'c':
            hmax = hmax * 2

        xmin = self.x_cur
        xmax = xmin + self.x_width - 1

        print(xmin, xmax)
        # ax2.set_xlim(xmin, xmax)
        self.ax_2d.set_data(self.spec_data[:, xmin:xmax])
        self.ax_2d.set_clim(hmin, hmax)
        self.fig.canvas.draw()


if __name__ == '__main__':
    input_path = r'specg.mat'

    win1 = WaveViewer(input_path)
    win1.wave_viewer()
