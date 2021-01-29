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
import hdf5storage
from PyQt5 import QtCore


def press(event):
    '''
    press
    '''
    print('press', event.key)
    sys.stdout.flush()

    xmin, xmax = ax.get_xlim()
    shift = (xmax - xmin)/16
    hmin, hmax = im.get_clim()

    if event.key == 'down':
        xmin = xmin * 2
        xmax = xmax * 2
    if event.key == 'up':
        xmin = xmin / 2
        xmax = xmax / 2
    if event.key == 'left':
        xmin = xmin + shift
        xmax = xmax + shift
    if event.key == 'right':
        xmin = xmin - shift
        xmax = xmax - shift
    if event.key == 'h':
        hmax = hmax / 2
    if event.key == 'c':
        hmax = hmax * 2

    ax.set_xlim(xmin, xmax)
    ax1.set_xlim(xmin, xmax)
    ax2.set_xlim(xmin, xmax)
    im.set_clim(hmin, hmax)
    fig.canvas.draw()
    fig1.canvas.draw()
    fig2.canvas.draw()


mat_path = r'W:\wataru\Recording_Analysis\Bases_dmPFC-BLA\2017-12-19_vm81a_base\RIG01_171219_140419_gamma.mat'
gamma = hdf5storage.loadmat(mat_path)['gamma']
data = np.squeeze(gamma['data'])[:, 0]
timestamps = np.squeeze(gamma['timestamps'])

mat_path = r'W:\wataru\Recording_Analysis\Bases_dmPFC-BLA\2017-12-19_vm81a_base\RIG01_171219_140419_specg_flat.mat'

spec = hdf5storage.loadmat(mat_path)

# list keys of dictionary
# print(spec.keys())

spec_data = np.squeeze(spec['powspctrm'][0, :, :])
spec_timestamps = np.squeeze(spec['time'])
spec_freq = np.squeeze(spec['freq'])

# print(spec_data.dtype, spec_data.shape, spec_timestamps.dtype,
#       spec_timestamps.shape, spec_freq.dtype, spec_freq.shape)

d_freq = (spec_freq[-1] - spec_freq[0])/(len(spec_freq)-1)/2
d_timestamps = (spec_timestamps[-1] -
                spec_timestamps[0])/(len(spec_timestamps)-1)/2
extent = [spec_timestamps[0]-d_timestamps, spec_timestamps[-1] +
          d_timestamps, spec_freq[0]-d_freq, spec_freq[-1]+d_freq]


# mat_path = r'W:\wataru\Recording_Analysis\Bases_dmPFC-BLA\2017-12-19_vm81a_base\RIG01_171219_140419_specg1.mat'
# specg1 = hdf5storage.loadmat(mat_path)['specg1']

# data_s = np.squeeze(specg1['powspctrm'][0, 0, :, :])
# timestamps_s = np.squeeze(specg1['time'])
# freq = np.squeeze(specg1['freq'])

# d_freq = (freq[-1] - freq[0])/(len(freq)-1)/2
# d_timestamps_s = (timestamps_s[-1] - timestamps_s[0])/(len(timestamps_s)-1)/2
# extent = [timestamps_s[0]-d_timestamps_s, timestamps_s[-1] +
#           d_timestamps_s, freq[0]-d_freq, freq[-1]+d_freq]


mpl.rcParams['toolbar'] = 'None'

###############################################################
fig = plt.figure()
ax = plt.subplot()
ax.set_xlim(2000, 2010)
#ax = fig.add_subplot(111, aspect='equal')
plt.subplots_adjust(left=0.05, bottom=0, right=1, top=1, wspace=0, hspace=0)
# fig, ax = plt.subplots()
fig.canvas.mpl_connect('key_press_event', press)
fig.canvas.toolbar_visible = False
fig.canvas.header_visible = False
fig.canvas.footer_visible = False
fig.canvas.window().statusBar().setVisible(False)
fig.set_size_inches(10, 2)
ax.plot(timestamps, data, linewidth=0.5)
# fig.canvas.manager.window.move(0, 0)

mngr = plt.get_current_fig_manager()
geom = mngr.window.geometry()
x_1, y_1, dx_1, dy_1 = geom.getRect()
mngr.window.setGeometry(0, 100, dx_1, dy_1)
mngr.window.setWindowFlags(QtCore.Qt.FramelessWindowHint)

###############################################################
fig1 = plt.figure()
ax1 = fig1.add_subplot()
ax1.set_xlim(2000, 2010)
#ax1 = fig1.add_subplot(111, aspect='equal')
plt.subplots_adjust(left=0.05, bottom=0, right=1, top=1, wspace=0, hspace=0)
# fig, ax = plt.subplots()
fig1.canvas.mpl_connect('key_press_event', press)
fig1.canvas.toolbar_visible = False
fig1.canvas.header_visible = False
fig1.canvas.footer_visible = False
fig1.canvas.window().statusBar().setVisible(False)
fig1.set_size_inches(10, 2)
ax1.plot(timestamps, data, linewidth=0.5)
# fig1.canvas.manager.window.move(0, 200)

mngr = plt.get_current_fig_manager()
geom = mngr.window.geometry()
x_2, y_2, dx_2, dy_2 = geom.getRect()
mngr.window.setGeometry(0, 100+dy_1, dx_2, dy_2)
mngr.window.setWindowFlags(QtCore.Qt.FramelessWindowHint)

###############################################################
fig2 = plt.figure()
ax2 = plt.subplot()
ax2.set_xlim(2000, 2010)
#ax = fig.add_subplot(111, aspect='equal')
plt.subplots_adjust(left=0.05, bottom=0, right=1, top=1, wspace=0, hspace=0)
# fig, ax = plt.subplots()
fig2.canvas.mpl_connect('key_press_event', press)
fig2.canvas.toolbar_visible = False
fig2.canvas.header_visible = False
fig2.canvas.footer_visible = False
fig2.canvas.window().statusBar().setVisible(False)
fig2.set_size_inches(10, 2)
# im = ax2.imshow(spec_data, extent=extent, cmap=plt.cm.jet,
#                 aspect='auto', interpolation='gaussian')

im = ax2.imshow(spec_data, extent=extent, cmap=plt.cm.jet,
                aspect='auto')

# plt.colorbar(im)
im.set_clim(0, 1000)

mngr = plt.get_current_fig_manager()
geom = mngr.window.geometry()
x_3, y_3, dx_3, dy_3 = geom.getRect()
mngr.window.setGeometry(0, 100+dy_1+dy_3, dx_3, dy_3)
mngr.window.setWindowFlags(QtCore.Qt.FramelessWindowHint)


# xl = ax.set_xlabel('easy come, easy go')
# ax.set_title('Press a key')
plt.show()
