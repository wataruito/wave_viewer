'''
plot02.py
hard coding to synchronize two figure
Only one core reaches to max
Try to hide win10 title bar, but it does not work.
'''
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from PyQt5 import QtCore
import hdf5storage


def wave_viewer():
    '''
    wave_viewer()
    '''
    global xmin, xmax, x_width, x_cur, im, spec_data, fig2

    # read spectrogram
    mat_path = r'specg.mat'

    spec = hdf5storage.loadmat(mat_path)
    spec_data = np.squeeze(spec['powspctrm'][0, :, :])
    spec_timestamps = np.squeeze(spec['time'])
    spec_freq = np.squeeze(spec['freq'])

    mpl.rcParams['toolbar'] = 'None'

    ###############################################################
    fig2 = plt.figure()
    ax2 = plt.subplot()
    # ax2.set_xlim(2000, 2010)
    #ax = fig.add_subplot(111, aspect='equal')
    plt.subplots_adjust(left=0.05, bottom=0, right=1,
                        top=1, wspace=0, hspace=0)
    # fig, ax = plt.subplots()
    fig2.canvas.mpl_connect('key_press_event', press)
    fig2.canvas.toolbar_visible = False
    fig2.canvas.header_visible = False
    fig2.canvas.footer_visible = False
    fig2.canvas.window().statusBar().setVisible(False)
    fig2.set_size_inches(10, 2)
    # im = ax2.imshow(spec_data, extent=extent, cmap=plt.cm.jet,
    #                 aspect='auto', interpolation='gaussian')

    im = ax2.imshow(spec_data[:, xmin:xmax], cmap=plt.cm.jet,
                    aspect='auto')

    # im = ax2.imshow(spec_data, extent=extent, cmap=plt.cm.jet,
    #                 aspect='auto')

    # plt.colorbar(im)
    im.set_clim(0, 1000)

    mngr = plt.get_current_fig_manager()
    geom = mngr.window.geometry()
    _, _, dx_3, dy_3 = geom.getRect()
    mngr.window.setGeometry(0, 100, dx_3, dy_3)
    mngr.window.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    # xl = ax.set_xlabel('easy come, easy go')
    # ax.set_title('Press a key')
    plt.show()


def press(event):
    '''
    press
    '''
    global xmin, xmax, x_width, x_cur, im, spec_data, fig2

    print('press', event.key)
    sys.stdout.flush()

    shift = int((xmax - xmin)/16)
    hmin, hmax = im.get_clim()

    if event.key == 'down':
        x_width = x_width * 2
    if event.key == 'up':
        x_width = int(x_width / 2)
    if event.key == 'left':
        x_cur = x_cur + shift
    if event.key == 'right':
        x_cur = x_cur - shift
    if event.key == 'h':
        hmax = hmax / 2
    if event.key == 'c':
        hmax = hmax * 2

    xmin = x_cur
    xmax = xmin + x_width - 1

    print(xmin, xmax)
    # ax2.set_xlim(xmin, xmax)
    im.set_data(spec_data[:, xmin:xmax])
    im.set_clim(hmin, hmax)
    fig2.canvas.draw()


if __name__ == '__main__':

    x_width = 100
    x_cur = 0
    xmin = x_cur
    xmax = xmin + x_width - 1

    wave_viewer()
