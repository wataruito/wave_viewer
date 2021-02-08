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


class WaveViewerMaster():
    '''
    WaveViewer
    '''

    def __init__(self, process_list, win_geom):
        '''
        '''
        self.process_list = process_list
        self.fig = []
        # self.win_size = [10.0, 0.5]     # window size in inch
        # self.win_pos = [0, 20]           # window position in pixel
        self.win_geom = win_geom

    def run(self):
        '''
        wave_viewer()
        '''
        # create window
        mpl.rcParams['toolbar'] = 'None'    # need to put here to hide toolbar
        self.fig = plt.figure()
        # self.fig.set_size_inches(self.win_size[0], self.win_size[1])
        self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = False
        self.fig.canvas.window().statusBar().setVisible(False)

        # move window position and remove title bar
        mngr = plt.get_current_fig_manager()
        # geom = mngr.window.geometry()
        # _, _, x_len, y_len = geom.getRect()
        mngr.window.setGeometry(*self.win_geom)

        plt.show()

    def press(self, event):
        '''
        press
        '''
        # print('press', event.key)
        sys.stdout.flush()

        for _process_id_key in self.process_list:
            self.process_list[_process_id_key][1].put(event.key)
        for _process_id_key in self.process_list:
            self.process_list[_process_id_key][1].join()

        if event.key == 'e':
            plt.close(self.fig)


class WaveViewer(multiprocessing.Process):
    '''
    WaveViewer
    '''

    def __init__(self, task_queue, result_queue, w_id, mat_path, d_type, win_geom):
        '''
        '''
        multiprocessing.Process.__init__(self)
        # self.namespace = namespace
        # self.event = event
        # self.process_list = []

        self.task_queue = task_queue
        self.result_queue = result_queue

        self.mat_path = mat_path
        self.d_type = d_type
        self.w_id = w_id
        # self.master = master

        self.x_width = 3195
        self.x_cur = 0
        self.hmin, self.hmax = 0.0, 8192000.0

        self.wave_data = []
        self.timestamps = []

        self.fig = []
        self.ax_subplot = []
        self.ax_plot = []

        # self.win_geom = [10.0, 2.0]
        self.win_geom = win_geom

    def run(self):
        '''
        wave_viewer()
        '''
        # create window
        mpl.rcParams['toolbar'] = 'None'    # need to put here to hide toolbar
        self.fig = plt.figure()
        # self.fig.set_size_inches(self.win_size[0], self.win_size[1])
        # self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = False
        self.fig.canvas.window().statusBar().setVisible(False)

        # move window position and remove title bar
        mngr = plt.get_current_fig_manager()
        # geom = mngr.window.geometry()
        # _, _, x_len, y_len = geom.getRect()
        # if self.master:
        #     mngr.window.setGeometry(
        #         0, 100 + self.w_id * y_len,
        #         x_len, int(y_len*1.1111))
        # else:
        #     mngr.window.setGeometry(
        #         0, 100 + self.w_id * y_len,
        #         x_len, y_len)
        mngr.window.setGeometry(*self.win_geom)
        mngr.window.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # create subplot
        self.ax_subplot = plt.subplot()

        # Define plotting area. It determine either show up axis or not
        bottom = 0.0  # DEBUG for x-scale. Nomal is bottom = 0
        # bottom = 0.2  # DEBUG for x-scale. Nomal is bottom = 0
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

            if self.d_type == 'wave':
                self.ax_plot, = self.ax_subplot.plot(
                    self.timestamps[xmin:xmax], self.wave_data[xmin:xmax], linewidth=0.5)
                self.ax_subplot.set_xlim(
                    self.timestamps[xmin], self.timestamps[xmax])

            if self.d_type == 'x_axis':
                self.ax_plot, = self.ax_subplot.plot(
                    self.timestamps[xmin:xmax], [0 for i in range(xmin, xmax)], linewidth=0)
                self.ax_subplot.set_xlim(
                    self.timestamps[xmin], self.timestamps[xmax])

                plt.subplots_adjust(left=0.05, right=1,
                                    bottom=0.99, top=1,
                                    wspace=0, hspace=0)
                plt.yticks([])

            # if not self.master:
        timer = self.fig.canvas.new_timer(interval=10)
        timer.add_callback(self.call_back)
        timer.start()

        plt.show()

    def call_back(self):
        '''
        call_back()
        '''
        if not self.task_queue.empty():
            next_task = self.task_queue.get()
            self.press(next_task)
            self.task_queue.task_done()
        return True

    def press(self, event):
        '''
        press
        '''
        # print(self.process_list)
        # print('press', event.key)
        sys.stdout.flush()

        if hasattr(event, 'key'):
            event = event.key

        shift = int(self.x_width/16)

        if self.d_type == 'spec':
            x_size = self.timestamps.size - 1
        else:
            x_size = int(self.timestamps.size / 10)

        if event == 'right':
            self.x_cur = self.x_cur + shift
            if self.x_cur + self.x_width - 1 > (x_size - 1):
                self.x_cur = (x_size - 1) - self.x_width + 1
        elif event == 'left':
            self.x_cur = self.x_cur - shift
            if self.x_cur < 0:
                self.x_cur = 0
        elif event == 'up':
            self.x_width = self.x_width * 2
            if self.x_cur + self.x_width - 1 > (x_size - 1):
                self.x_cur = (x_size - 1) - self.x_width + 1
            if self.x_cur < 0:
                self.x_cur = 0
            if self.x_cur + self.x_width - 1 > (x_size - 1):
                self.x_width = (x_size - 1)
        elif event == 'down':
            self.x_width = int(self.x_width / 2)
        elif event == 'h':  # hotter
            self.hmax = self.hmax / 2
        elif event == 'c':  # cooler
            self.hmax = self.hmax * 2
        elif event == 'e':
            plt.close(self.fig)

        xmin = self.x_cur
        xmax = self.x_cur + self.x_width - 1

        if self.d_type == 'spec':
            extent = [self.timestamps[xmin],
                      self.timestamps[xmax], 0, 200]

            # print('press', event, ': ', xmin, xmax, self.hmax)
            self.ax_plot.set_data(self.wave_data[:, xmin:xmax])
            self.ax_plot.set_clim(self.hmin, self.hmax)
            self.ax_plot.set_extent(extent)
        else:
            xmin *= 10
            xmax *= 10

            # print('press', event, ': ', xmin, xmax)
            self.ax_plot.set_data(
                self.timestamps[xmin:xmax], self.wave_data[xmin:xmax])
            # self.ax_subplot.relim()
            self.ax_subplot.set_xlim(
                self.timestamps[xmin], self.timestamps[xmax])
            self.ax_subplot.autoscale_view(True, True, True)

        self.fig.canvas.draw()


if __name__ == '__main__':

    # open windows for each waves and specs
    process_members = [
        [0, r'RIG01_171219_140419_specg_flat.mat',
            'spec', (0, 100, 1000, 100)],
        [1, r'RIG01_171219_140419_lfp_flat.mat', 'wave', (0, 200, 1000, 100)],
        [2, r'RIG01_171219_140419_gamma_flat.mat',
            'wave', (0, 300, 1000, 100)],
        [3, r'RIG01_171219_140419_gamma_flat.mat',
            'wave', (0, 400, 1000, 100)],
        [4, r'RIG01_171219_140419_gamma_flat.mat',
            'wave', (0, 500, 1000, 100)],
        [5, r'RIG01_171219_140419_gamma_flat.mat',
            'wave', (0, 600, 1000, 100)],
        [6, r'RIG01_171219_140419_gamma_flat.mat',
            'x_axis', (0, 700, 1000, 30)]
    ]

    input_process_list = {}

    for process in process_members:
        task = multiprocessing.JoinableQueue()
        result = multiprocessing.Queue()

        # input_tuple = (process[0], process[1], process[2], process[3])
        input_tuple = tuple(process)

        process_id = WaveViewer(task, result, *input_tuple)
        process_id.start()
        print('Started: ', process_id)

        input_process_list[str(process[0])] = (process_id, task, result)

    # open master window for control
    masterWin = WaveViewerMaster(input_process_list, (0, 20, 1000, 80))
    masterWin.run()

    # wait until all processes stop
    for _process_id_key in input_process_list:
        input_process_list[_process_id_key][0].join()
