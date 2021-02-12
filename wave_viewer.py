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

        self.t_width = 10.0
        self.t_cur = 10.0

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

        self.create_window()

        if self.d_type == 'spec':
            self.disp_2d()
        else:
            self.disp_1d()

        # start timer
        # if not self.master:
        timer = self.fig.canvas.new_timer(interval=10)
        timer.add_callback(self.timer_call_back)
        timer.start()

        # draw glid
        # plt.grid(ls='--', lw=0.25)
        plt.show()

    def create_window(self):
        '''
        create_window
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
        # bottom = 0.0  # DEBUG for x-scale. Nomal is bottom = 0
        bottom = 0.2  # DEBUG for x-scale. Nomal is bottom = 0
        plt.subplots_adjust(left=0.05, right=1,
                            bottom=bottom, top=1,
                            wspace=0, hspace=0)

        plt.grid(ls='--', lw=0.25)

    def disp_2d(self):
        '''
        disp_2d
        '''
        # read spectrogram
        spec = hdf5storage.loadmat(self.mat_path)
        self.wave_data = np.squeeze(spec['powspctrm'][0, :, :])
        self.timestamps = np.squeeze(spec['time'])
        spec_freq = np.squeeze(spec['freq'])

        # compute extent
        t_min = self.t_cur - self.t_width/2
        t_max = self.t_cur + self.t_width/2
        _, xmin = self.find_nearest(self.timestamps, t_min)
        _, xmax = self.find_nearest(self.timestamps, t_max)
        extent = [t_min, t_max, 0, 200]

        # show 2D image
        self.ax_plot = self.ax_subplot.imshow(self.wave_data[:, xmin:xmax],
                                              extent=extent, cmap=plt.cm.jet,
                                              origin='lower',
                                              aspect='auto')

        self.ax_subplot.set_xlim(t_min, t_max)

        # set color level
        # plt.colorbar(im)
        self.ax_plot.set_clim(self.hmin, self.hmax)

        # create y tick labels
        spec_y = np.arange(0, 201, 25)
        spec_y_value = spec_freq[spec_y].astype(int)
        self.ax_subplot.set_yticks(spec_y)
        self.ax_subplot.set_yticklabels(spec_y_value)

    def disp_1d(self):
        '''
        disp_1d
        '''
        # read wave
        wave = hdf5storage.loadmat(self.mat_path)
        self.wave_data = np.squeeze(wave['data'])[:, 0]
        self.timestamps = np.squeeze(wave['timestamps'])

        # compute extent
        t_min = self.t_cur - self.t_width/2
        t_max = self.t_cur + self.t_width/2
        _, xmin = self.find_nearest(self.timestamps, t_min)
        _, xmax = self.find_nearest(self.timestamps, t_max)

        # plot wave or x_axis
        if self.d_type == 'wave':
            self.ax_plot, = self.ax_subplot.plot(
                self.timestamps[xmin:xmax], self.wave_data[xmin:xmax], linewidth=0.5)

        if self.d_type == 'x_axis':
            self.ax_plot, = self.ax_subplot.plot(
                self.timestamps[xmin:xmax], np.full(xmax-xmin, 0), linewidth=0)

            plt.subplots_adjust(left=0.05, right=1,
                                bottom=0.99, top=1,
                                wspace=0, hspace=0)
            plt.yticks([])

        self.ax_subplot.set_xlim(t_min, t_max)

    def timer_call_back(self):
        '''
        call_back()
        '''
        if not self.task_queue.empty():
            next_task = self.task_queue.get()
            self.update_extent(next_task)
            self.update_plot()
            self.task_queue.task_done()
        return True

    def find_nearest(self, array, value):
        '''
        find_nearest
        '''
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx], idx

    def update_extent(self, event):
        '''
        press
        '''
        # print(self.process_list)
        # print('press', event.key)
        sys.stdout.flush()

        if hasattr(event, 'key'):
            event = event.key

        shift = self.t_width/16.0

        if event == 'right':
            self.t_cur = self.t_cur + shift
        elif event == 'left':
            self.t_cur = self.t_cur - shift
        elif event == 'up':
            self.t_width = self.t_width * 2.0
        elif event == 'down':
            self.t_width = self.t_width / 2.0
        elif event == 'h':  # hotter
            self.hmax = self.hmax / 2
        elif event == 'c':  # cooler
            self.hmax = self.hmax * 2
        elif event == 'e':
            plt.close(self.fig)

        if self.t_width > 3600.0:
            self.t_width = 3600.0
        if self.t_cur + self.t_width/2.0 > 3600.0:
            self.t_cur = 3600.0 - self.t_width/2.0
        if self.t_cur - self.t_width/2.0 < 0.0:
            self.t_cur = 0.0 + self.t_width/2.0

    def update_plot(self):
        # compute extent
        t_min = self.t_cur - self.t_width/2
        t_max = self.t_cur + self.t_width/2
        _, xmin = self.find_nearest(self.timestamps, t_min)
        _, xmax = self.find_nearest(self.timestamps, t_max)

        if self.d_type == 'spec':
            extent = [t_min, t_max, 0, 200]

            # print('press', event, ': ', xmin, xmax, self.hmax)
            self.ax_plot.set_data(self.wave_data[:, xmin:xmax])
            self.ax_plot.set_clim(self.hmin, self.hmax)
            self.ax_plot.set_extent(extent)
            self.ax_subplot.set_xlim(t_min, t_max)

        else:
            # print('press', event, ': ', xmin, xmax)
            self.ax_plot.set_data(
                self.timestamps[xmin:xmax], self.wave_data[xmin:xmax])
            # self.ax_subplot.relim()
            self.ax_subplot.set_xlim(t_min, t_max)
            self.ax_subplot.autoscale_view(True, True, True)

        self.fig.canvas.draw()


if __name__ == '__main__':

    # open windows for each waves and specs
    # process_members = [
    #     [0, r'input_data\RIG01_171219_140419_specg_flat.mat',
    #         'spec', (0, 100, 1000, 100)],
    #     [1, r'input_data\RIG01_171219_140419_lfp_flat.mat',
    #         'wave', (0, 200, 1000, 100)],
    #     [2, r'input_data\RIG01_171219_140419_gamma_flat.mat',
    #         'wave', (0, 300, 1000, 100)],
    #     [3, r'input_data\RIG01_171219_140419_gamma_flat.mat',
    #         'wave', (0, 400, 1000, 100)],
    #     [4, r'input_data\RIG01_171219_140419_gamma_flat.mat',
    #         'wave', (0, 500, 1000, 100)],
    #     [5, r'input_data\RIG01_171219_140419_gamma_flat.mat',
    #         'wave', (0, 600, 1000, 100)],
    #     [6, r'input_data\RIG01_171219_140419_gamma_flat.mat',
    #         'x_axis', (0, 700, 1000, 30)]
    # ]

    process_members = [
        [0, r'input_data\short_specg_flat.mat',
         'spec', (0, 100, 1000, 100)],
        [1, r'input_data\short_gamma_flat.mat',
         'wave', (0, 200, 1000, 100)],
        [6, r'input_data\RIG01_171219_140419_gamma_flat.mat',
         'x_axis', (0, 300, 1000, 30)]
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
