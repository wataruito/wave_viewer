'''
wave-viewer.py
'''

import sys
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from PyQt5 import QtCore
import hdf5storage


class WaveViewer(multiprocessing.Process):
    '''
    WaveViewer
    '''

    def __init__(self, task_queue, result_queue, mat_path, d_type, w_id, master):
        '''
        '''
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

        self.mat_path = mat_path
        self.d_type = d_type
        self.w_id = w_id
        self.master = master

        self.x_width = 3195
        self.x_cur = 0
        self.hmin, self.hmax = 0.0, 8192000.0

        self.wave_data = []
        self.timestamps = []

        self.fig = []
        self.ax_subplot = []
        self.ax_plot = []

        self.win_size = [10.0, 2.0]

    def run(self):
        '''
        wave_viewer()
        '''

        # create window
        mpl.rcParams['toolbar'] = 'None'    # need to put here to hide toolbar
        self.fig = plt.figure()
        self.fig.set_size_inches(self.win_size[0], self.win_size[1])
        self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = False
        self.fig.canvas.window().statusBar().setVisible(False)

        # move window position and remove title bar
        mngr = plt.get_current_fig_manager()
        geom = mngr.window.geometry()
        _, _, x_len, y_len = geom.getRect()
        if self.master:
            mngr.window.setGeometry(
                0, 100 + self.w_id * y_len,
                x_len, int(y_len*1.1111))
        else:
            mngr.window.setGeometry(
                0, 100 + self.w_id * y_len,
                x_len, y_len)
        mngr.window.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # create subplot
        self.ax_subplot = plt.subplot()
        if self.master:
            bottom = 0.1
        else:
            bottom = 0.1  # DEBUG for x-scale. Nomal is bottom = 0
        plt.subplots_adjust(left=0.05, right=1,
                            bottom=bottom, top=1,
                            wspace=0, hspace=0)

        if self.d_type == 'spec':
            # read spectrogram
            spec = hdf5storage.loadmat(self.mat_path)
            self.wave_data = np.squeeze(spec['powspctrm'][0, :, :])
            self.timestamps = np.squeeze(spec['time'])
            spec_freq = np.squeeze(spec['freq'])

            # create y tick labels
            spec_y = np.arange(0, 201, 25)
            spec_y_value = spec_freq[spec_y].astype(int)

            # compute extent
            xmin = self.x_cur
            xmax = xmin + self.x_width - 1
            extent = [self.timestamps[xmin],
                      self.timestamps[xmax], 0, 200]

            # show 2D image
            self.ax_plot = self.ax_subplot.imshow(self.wave_data[:, xmin:xmax],
                                                  extent=extent, cmap=plt.cm.jet,
                                                  origin='lower',
                                                  aspect='auto')
            # adjust 2D image
            # plt.colorbar(im)
            self.ax_plot.set_clim(self.hmin, self.hmax)
            self.ax_subplot.set_yticks(spec_y)
            self.ax_subplot.set_yticklabels(spec_y_value)

        else:
            # read wave
            wave = hdf5storage.loadmat(self.mat_path)
            self.wave_data = np.squeeze(wave['data'])[:, 0]
            self.timestamps = np.squeeze(wave['timestamps'])

            # compute extent
            xmin = self.x_cur
            xmax = xmin + self.x_width - 1
            xmin *= 10
            xmax *= 10

            # plot wave
            self.ax_plot, = self.ax_subplot.plot(
                self.timestamps[xmin:xmax], self.wave_data[xmin:xmax], linewidth=0.5)
            self.ax_subplot.set_xlim(
                self.timestamps[xmin], self.timestamps[xmax])

        plt.show()

    def press(self, event):
        '''
        press
        '''

        # print('press', event.key)
        sys.stdout.flush()

        shift = int(self.x_width/16)

        if self.d_type == 'spec':
            x_size = self.timestamps.size - 1
        else:
            x_size = int(self.timestamps.size / 10)

        if event.key == 'right':
            self.x_cur = self.x_cur + shift
            if self.x_cur + self.x_width - 1 > (x_size - 1):
                self.x_cur = (x_size - 1) - self.x_width + 1
        elif event.key == 'left':
            self.x_cur = self.x_cur - shift
            if self.x_cur < 0:
                self.x_cur = 0
        elif event.key == 'up':
            self.x_width = self.x_width * 2
            if self.x_cur + self.x_width - 1 > (x_size - 1):
                self.x_cur = (x_size - 1) - self.x_width + 1
            if self.x_cur < 0:
                self.x_cur = 0
            if self.x_cur + self.x_width - 1 > (x_size - 1):
                self.x_width = (x_size - 1)
        elif event.key == 'down':
            self.x_width = int(self.x_width / 2)
        elif event.key == 'h':
            self.hmax = self.hmax / 2
        elif event.key == 'c':
            self.hmax = self.hmax * 2
        elif event.key == 'e':
            plt.close(self.fig)

        xmin = self.x_cur
        xmax = self.x_cur + self.x_width - 1

        if self.d_type == 'spec':
            extent = [self.timestamps[xmin],
                      self.timestamps[xmax], 0, 200]

            print('press', event.key, ': ', xmin, xmax, self.hmax)
            self.ax_plot.set_data(self.wave_data[:, xmin:xmax])
            self.ax_plot.set_clim(self.hmin, self.hmax)
            self.ax_plot.set_extent(extent)
        else:
            xmin *= 10
            xmax *= 10

            print('press', event.key, ': ', xmin, xmax)
            self.ax_plot.set_data(
                self.timestamps[xmin:xmax], self.wave_data[xmin:xmax])
            # self.ax_subplot.relim()
            self.ax_subplot.set_xlim(
                self.timestamps[xmin], self.timestamps[xmax])
            self.ax_subplot.autoscale_view(True, True, True)

        self.fig.canvas.draw()


if __name__ == '__main__':

    input_path_list = [
        r'specg_flat.mat',
        r'gamma_flat.mat'
    ]

    input_d_type_list = [
        'spec',
        'gamma'
    ]

    input_master_list = [
        False,
        True
    ]

    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()

    waveviewers = [WaveViewer(
        tasks, results, input_path_list[i], input_d_type_list[i], i, input_master_list[i]) for i in range(2)]

    for w in waveviewers:

        w.start()
        print(w)

    tasks.join()
