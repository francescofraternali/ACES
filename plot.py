import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from subprocess import PIPE, Popen, call
from datetime import datetime, timedelta
import os
import threading
import subprocess
import time


def extract(path):
    Time_hist = []; Volt_hist = []; Perf_hist = []; PIR_hist = []; Light_hist = [];
    start = datetime.now() - timedelta(days=1)
    with open(path, 'r') as f:
        for line in f:
            try:
                Splitted = line.split("|");
                time = datetime.strptime(Splitted[0], '%m/%d/%y %H:%M:%S')
                if time >= start:
                    SC_Pure = int(Splitted[5])
                    Light = int(Splitted[8])
                    perf = int(Splitted[4])
                    PIR = int(Splitted[6])

                    if SC_Pure == 0 and Light == 0 and perf == 0 and PIR == 0:
                        pass
                    else:
                        SC = SC_Pure
                        Time_hist.append(time); Volt_hist.append(SC); Perf_hist.append(perf); PIR_hist.append(PIR); Light_hist.append(Light)
            except:
                pass

    return Time_hist, Volt_hist, Perf_hist, PIR_hist, Light_hist

def plotting(Time_hist_1, Volt_hist_1, Perf_hist_1, PIR_hist_1, Light_hist_1, file_1, Time_hist_2, Volt_hist_2, Perf_hist_2, PIR_hist_2, Light_hist_2, file, fignum, show):

    #plt.figure(fignum)
    fig, ax = plt.subplots(1)
    #fig.set_size_inches(80, 60)
    #mngr = plt.get_current_fig_manager()
    #mngr.window.setPosition((500, 0))
    mng = plt.get_current_fig_manager()
    #mng.full_screen_toggle() 

    fig.autofmt_xdate()
    timer = fig.canvas.new_timer(interval = 20000)
    timer.add_callback(close_event)

    plt.subplot(4, 1, 1)
    plt.title(file_1 + ' - ' + file, fontsize=15)
    plt.grid(True)
    plt.plot(Time_hist_1, Volt_hist_1, 'r*', label = 'SC_Volt Real Black', markersize = 10)
    plt.plot(Time_hist_2, Volt_hist_2, 'k.', label = 'SC_Volt Real Red', markersize = 10)
    plt.ylabel('Super [V]\nCapacitor', fontsize=15)
    plt.ylim(42, 105)
    plt.legend(loc=9, prop={'size': 10})
    plt.subplot(4, 1, 2)
    plt.grid(True)
    plt.plot(Time_hist_1, Light_hist_1, 'b', label = 'Light Black', markersize = 10)
    plt.plot(Time_hist_2, Light_hist_2, 'k.', label = 'Light Red', markersize = 10)
    plt.ylabel('Light\n[lux]', fontsize=15)
    plt.legend(loc=9, prop={'size': 10})
    plt.subplot(4, 1, 3)
    plt.grid(True)
    plt.plot(Time_hist_1, PIR_hist_1, 'y*', label = 'PIR Black', markersize = 10)
    plt.plot(Time_hist_2, PIR_hist_2, 'k.', label = 'PIR Red', markersize = 10)
    plt.ylim(-1, 2)
    plt.ylabel('PIR\n[event]', fontsize=15)
    plt.legend(loc=9, prop={'size': 10})
    plt.subplot(4, 1, 4)
    plt.grid(True)
    plt.plot(Time_hist_1, Perf_hist_1, 'g*', label = 'Performance Black', markersize = 10)
    plt.plot(Time_hist_2, Perf_hist_2, 'k.', label = 'Performance Red', markersize = 10)
    plt.ylim(-1, 4)
    plt.legend(loc=9, prop={'size': 10})
    plt.ylabel('Performance\n[num]', fontsize=15)
    #plt.plot(Time_hist, SC_Pure_hist, 'b*')
    xfmt = mdates.DateFormatter('%m/%d %H')
    ax.xaxis.set_major_formatter(xfmt)
    ax.tick_params(axis='both', which='major', labelsize=15)
    #legend = ax.legend(loc='center right', shadow=True)
    #plt.legend(loc=9, prop={'size': 10})

    plt.xlabel('Time [day hour:min]', fontsize=20)
    timer.start()
    plt.show()
    #plt.draw()
    #if show == 1:
    #    #print('here')
    #    plt.show()



def close_event():
    plt.close()

path = "FF62_demo_sensor.txt"

file_1 = "Black Pible"
file = "Red Pible"


for step in range(0,100):
    Time_hist_1, Volt_hist_1, Perf_hist_1, PIR_hist_1, Light_hist_1 = extract(path)
    Time_hist_2 = []; Volt_hist_2 = []; Perf_hist_2 = []; PIR_hist_2 = []; Light_hist_2 = [];

    plotting(Time_hist_1, Volt_hist_1, Perf_hist_1, PIR_hist_1, Light_hist_1, file_1, Time_hist_2, Volt_hist_2, Perf_hist_2, PIR_hist_2, Light_hist_2, file, 1, 1)
    #time.sleep(1)
    
