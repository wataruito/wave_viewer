'''
wave-viewer.py

Simple viewer for neuronal recorded/processed data
    Capable to display > 1h data for
        spectrogram from fieldtrip
        PAC fA and fP map from BrainStorm
        LFP and band filtered data from BuzCode

Interface:
    input_files - specify input files
    window_geo - window size and initial position

    h: color hotter
    c: color cooler
    up: larger time range (shrink)
    down: smaller time range (magnify)
    left/right: move viewing window
'''
import math
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
        Master window
    '''

    def __init__(self, process_list, win_geom, max_time):
        '''
        '''
        self.process_list = process_list
        self.fig = []
        self.mngr = []

        self.win_geom = win_geom

        self.t_width = 10.0
        self.t_cur = 10.0
        self.max_time = max_time

    def run(self):
        '''
        wave_viewer()
        '''
        # create window
        mpl.rcParams['toolbar'] = 'None'    # need to put here to hide toolbar
        self.fig = plt.figure()
        self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = False
        self.fig.canvas.window().statusBar().setVisible(False)

        # move window position and remove title bar
        self.mngr = plt.get_current_fig_manager()
        self.mngr.window.setGeometry(*self.win_geom)

        plt.show()

    def press(self, event):
        '''
        press
        '''
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

        elif event == 'e':
            plt.close(self.fig)

        if self.t_width > self.max_time:
            self.t_width = self.max_time
        if self.t_cur + self.t_width/2.0 > self.max_time:
            self.t_cur = self.max_time - self.t_width/2.0
        if self.t_cur - self.t_width/2.0 < 0.0:
            self.t_cur = 0.0 + self.t_width/2.0

        # get position of master window
        geom = self.mngr.window.geometry()
        orig_x, orig_y, _, _ = geom.getRect()
        orig_y = orig_y - 20

        # send key and the extent to each process
        for _process_id_key in self.process_list:
            self.process_list[_process_id_key][1].put(event)
            if event in ('right', 'left', 'up', 'down'):
                self.process_list[_process_id_key][1].put(self.t_cur)
                self.process_list[_process_id_key][1].put(self.t_width)
            if event == 'm':
                orig_y = orig_y + 100
                self.process_list[_process_id_key][1].put(orig_x)
                self.process_list[_process_id_key][1].put(orig_y)

        # wait for completion of task
        for _process_id_key in self.process_list:
            self.process_list[_process_id_key][1].join()


class WaveViewer(multiprocessing.Process):
    '''
    WaveViewer
        Subordinate window
    '''

    def __init__(self, task_queue, result_queue, mat_path, d_type, chan_id, win_geom):
        '''
        '''
        multiprocessing.Process.__init__(self)

        self.task_queue = task_queue
        self.result_queue = result_queue

        self.mat_path = mat_path
        self.d_type = d_type
        self.chan_id = chan_id

        self.t_width = 10.0
        self.t_cur = 10.0

        self.hmin, self.hmax = 0.0, 0.0
        self.color_fac = 1.0

        self.wave_data = []
        self.timestamps = []
        self.spec_freq = []

        self.fig = []
        self.ax_subplot = []
        self.ax_plot = []
        self.mngr = []

        self.x_axis = False

        self.win_geom = win_geom
        self.orig_x, self.orig_y = win_geom[0], win_geom[1]

    def run(self):
        '''
        wave_viewer()
        '''

        self.create_window()

        if self.d_type in ('spec', 'paca', 'pacp'):
            self.disp_2d()
        else:
            self.disp_1d()

        # start timer for receiving message from master window
        timer = self.fig.canvas.new_timer(interval=10)
        timer.add_callback(self.timer_call_back)
        timer.start()

        plt.show()

    def create_window(self):
        '''
        create_window
        '''
        # create window
        mpl.rcParams['toolbar'] = 'None'    # need to put here to hide toolbar
        self.fig = plt.figure()
        self.fig.canvas.mpl_connect(
            'key_press_event', self.local_key_call_back)
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = False
        self.fig.canvas.window().statusBar().setVisible(False)

        # move window position and remove title bar
        self.mngr = plt.get_current_fig_manager()
        self.mngr.window.setGeometry(*self.win_geom)
        self.mngr.window.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # create subplot
        self.ax_subplot = plt.subplot()

        # Define plotting area. It determine either show up axis or not
        bottom = 0.0  # DEBUG for x-scale. Nomal is bottom = 0
        # bottom = 0.2  # DEBUG for x-scale. Nomal is bottom = 0
        plt.subplots_adjust(left=0.05, right=1,
                            bottom=bottom, top=1,
                            wspace=0, hspace=0)

        # show glids
        plt.grid(ls='--', lw=0.25)

    def disp_2d(self):
        '''
        disp_2d
        '''
        # read spectrogram
        spec = hdf5storage.loadmat(self.mat_path)
        self.wave_data = np.squeeze(spec['powspctrm'][self.chan_id, :, :])
        self.timestamps = np.squeeze(spec['time'])
        self.spec_freq = np.squeeze(spec['freq'])

        # compute extent
        t_min = self.t_cur - self.t_width/2
        t_max = self.t_cur + self.t_width/2
        _, xmin = self.find_nearest(self.timestamps, t_min)
        _, xmax = self.find_nearest(self.timestamps, t_max)

        extent = [t_min, t_max, math.log(
            self.spec_freq[0], 2.0), math.log(self.spec_freq[-1], 2.0)]
        # extent = [t_min, t_max, 0, 200]

        # show 2D image
        self.ax_plot = self.ax_subplot.imshow(self.wave_data[:, xmin:xmax],
                                              extent=extent, cmap=plt.cm.jet,
                                              origin='lower',
                                              aspect='auto')

        self.ax_subplot.set_xlim(t_min, t_max)

        # set color level
        # plt.colorbar(im)
        if self.d_type == 'spec':
            self.hmin, self.hmax = 0.0, 8192000.0
            self.color_fac = 2.0
        if self.d_type == 'paca':
            self.hmin, self.hmax = 0.0, 0.5
            self.color_fac = 1.2
        if self.d_type == 'pacp':
            self.hmin, self.hmax = 0.0, 0.000001
            self.color_fac = 1.2

        self.ax_plot.set_clim(self.hmin, self.hmax)

        # create y tick labels
        spec_y = np.arange(
            math.log(self.spec_freq[0], 2),
            math.log(self.spec_freq[-1], 2) -
            math.fmod(math.log(self.spec_freq[-1], 2), 1) + 1
        ).astype(int)
        spec_y_value = 2**spec_y

        # spec_y = np.arange(0, 201, 25)
        # spec_y_value = spec_freq[spec_y].astype(int)

        self.ax_subplot.set_yticks(spec_y)
        self.ax_subplot.set_yticklabels(spec_y_value)

    def disp_1d(self):
        '''
        disp_1d
        '''
        # read wave
        wave = hdf5storage.loadmat(self.mat_path)
        self.wave_data = np.squeeze(wave['data'])[:, self.chan_id]
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
            if next_task in ('right', 'left', 'up', 'down'):
                self.t_cur = self.task_queue.get()
                self.task_queue.task_done()
                self.t_width = self.task_queue.get()
                self.task_queue.task_done()
                self.update_plot()
            elif next_task == 'm':
                self.orig_x = self.task_queue.get()
                self.task_queue.task_done()
                self.orig_y = self.task_queue.get()
                self.task_queue.task_done()
                self.move_window()
            else:
                self.cmd_interp(next_task)
                self.update_plot()

            self.task_queue.task_done()
        return True

    def local_key_call_back(self, event):
        '''
        local_key_call_back
        '''
        sys.stdout.flush()

        if hasattr(event, 'key'):
            event = event.key
        if event != 'e':
            self.cmd_interp(event)
            self.update_plot()

    def find_nearest(self, array, value):
        '''
        find_nearest
        '''
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx], idx

    def cmd_interp(self, event):
        '''
        press
        '''
        if event == 'h':  # hotter
            self.hmax = self.hmax / self.color_fac
        elif event == 'c':  # cooler
            self.hmax = self.hmax * self.color_fac
        elif event == 'x':
            self.x_axis = not self.x_axis
        elif event == 'e':
            plt.close(self.fig)

    def update_plot(self):
        '''
        update_plot
        '''
        # compute extent
        t_min = self.t_cur - self.t_width/2
        t_max = self.t_cur + self.t_width/2
        _, xmin = self.find_nearest(self.timestamps, t_min)
        _, xmax = self.find_nearest(self.timestamps, t_max)

        if self.d_type in ('spec', 'paca', 'pacp'):
            # extent = [t_min, t_max, 0, 200]
            extent = [t_min, t_max, math.log(
                self.spec_freq[0], 2.0), math.log(self.spec_freq[-1], 2.0)]

            self.ax_plot.set_data(self.wave_data[:, xmin:xmax])
            self.ax_plot.set_clim(self.hmin, self.hmax)
            self.ax_plot.set_extent(extent)
            self.ax_subplot.set_xlim(t_min, t_max)

        else:
            self.ax_plot.set_data(
                self.timestamps[xmin:xmax], self.wave_data[xmin:xmax])
            self.ax_subplot.relim()
            self.ax_subplot.set_xlim(t_min, t_max)
            self.ax_subplot.autoscale_view(True, True, True)

        if self.d_type != 'x_axis':
            if self.x_axis:
                bottom = 0.2
            else:
                bottom = 0.0
            plt.subplots_adjust(left=0.05, right=1,
                                bottom=bottom, top=1,
                                wspace=0, hspace=0)

        self.fig.canvas.draw()

    def move_window(self):
        '''
        move_window
        '''
        geom = self.mngr.window.geometry()
        _, _, x_len, y_len = geom.getRect()

        self.mngr.window.setGeometry(self.orig_x, self.orig_y, x_len, y_len)

        self.fig.canvas.draw()


def spawn_wins(process_members, window_spec):
    '''
    spawn_wins
    '''
    win_x_len = window_spec['win_x_len']
    win_y_len = window_spec['win_y_len']
    win_y_len_axis = window_spec['win_y_len_axis']
    win_x_origin = window_spec['win_x_origin']
    win_y_origin = window_spec['win_y_origin']

    process_list = {}
    process_list_num = 0
    for process in process_members:
        win_y_origin = win_y_origin + win_y_len
        if process[1] == 'x_axis':
            input_tuple = tuple(process) + \
                ((win_x_origin, win_y_origin, win_x_len, win_y_len_axis),)
        else:
            input_tuple = tuple(process) + \
                ((win_x_origin, win_y_origin, win_x_len, win_y_len),)

        # print(input_tuple)

    # for process in process_members:
        task = multiprocessing.JoinableQueue()
        result = multiprocessing.Queue()

        process_id = WaveViewer(task, result, *input_tuple)
        process_id.start()
        print('Started: ', process_id)

        process_list_num += 1
        process_list[str(process_list_num)] = (process_id, task, result)

    return process_list


if __name__ == '__main__':

    window_geo = {'win_x_len': 1000, 'win_y_len': 100, 'win_y_len_axis': 30,
                  'win_x_origin': 0, 'win_y_origin': 0}

    # open windows for each waves and specs
    input_files = [
        [r'input_data\RIG01_171219_140419_specg_flat.mat', 'spec', 0],
        [r'input_data\RIG01_171219_140419_irtpaca_flat.mat', 'paca', 0],
        [r'input_data\RIG01_171219_140419_irtpacp_flat.mat', 'pacp', 0],
        [r'input_data\RIG01_171219_140419_lfp_flat.mat', 'wave', 0],
        [r'input_data\RIG01_171219_140419_delta_flat.mat', 'wave', 0],
        [r'input_data\RIG01_171219_140419_theta_flat.mat', 'wave', 0],
        [r'input_data\RIG01_171219_140419_alphabeta_flat.mat', 'wave', 0],
        [r'input_data\RIG01_171219_140419_gamma_flat.mat', 'wave', 0],
        [r'input_data\RIG01_171219_140419_lfp_flat.mat', 'x_axis', 0]
    ]

    # start each window
    input_process_list = spawn_wins(input_files, window_geo)

    # open master window for control
    masterWin = WaveViewerMaster(input_process_list, (0, 20, 1000, 80), 3600.0)
    masterWin.run()

    # wait until all processes stop
    for _process_id_key in input_process_list:
        input_process_list[_process_id_key][0].join()

    # process_members = [
    #     [r'input_data\short_specg_flat.mat', 'spec', 0],
    #     [r'input_data\short_gamma_flat.mat', 'wave', 0],
    #     [r'input_data\RIG01_171219_140419_gamma_flat.mat', 'x_axis', 0]
    # ]

    # process_members = [
    #     [r'input_data\RIG01_171219_140419_irtpaca_flat.mat', 'paca', 0],
    #     [r'input_data\RIG01_171219_140419_gamma_flat.mat', 'x_axis', 0]
    # ]

    # process_members = [
    #     [r'input_data\RIG01_171219_140419_irtpacp_flat.mat', 'pacp', 0],
    #     [r'input_data\RIG01_171219_140419_gamma_flat.mat', 'x_axis', 0]
    # ]
