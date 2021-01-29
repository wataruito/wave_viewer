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

# read spectrogram
mat_path = r'W:\wataru\Recording_Analysis\Bases_dmPFC-BLA\2017-12-19_vm81a_base\RIG01_171219_140419_specg_flat.mat'

spec = hdf5storage.loadmat(mat_path)
spec_data = np.squeeze(spec['powspctrm'][0, :, :])
spec_timestamps = np.squeeze(spec['time'])
spec_freq = np.squeeze(spec['freq'])

# d_freq = (spec_freq[-1] - spec_freq[0])/(len(spec_freq)-1)/2
# d_timestamps = (spec_timestamps[-1] -
#                 spec_timestamps[0])/(len(spec_timestamps)-1)/2
# extent = [spec_timestamps[0]-d_timestamps, spec_timestamps[-1] +
#           d_timestamps, spec_freq[0]-d_freq, spec_freq[-1]+d_freq]


x_width = 100
x_cur = 0
xmin = x_cur
xmax = xmin + x_width - 1


def press(event):
    '''
    press
    '''
    global xmin, xmax, x_width, x_cur

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


mpl.rcParams['toolbar'] = 'None'

###############################################################
fig2 = plt.figure()
ax2 = plt.subplot()
# ax2.set_xlim(2000, 2010)
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


im = ax2.imshow(spec_data[:, xmin:xmax], cmap=plt.cm.jet,
                aspect='auto')

# im = ax2.imshow(spec_data, extent=extent, cmap=plt.cm.jet,
#                 aspect='auto')

# plt.colorbar(im)
im.set_clim(0, 1000)

mngr = plt.get_current_fig_manager()
geom = mngr.window.geometry()
x_3, y_3, dx_3, dy_3 = geom.getRect()
mngr.window.setGeometry(0, 100, dx_3, dy_3)
mngr.window.setWindowFlags(QtCore.Qt.FramelessWindowHint)


# xl = ax.set_xlabel('easy come, easy go')
# ax.set_title('Press a key')
plt.show()
