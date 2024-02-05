from datetime import datetime
from tkinter import *
import tkinter as tkinter
from tkinter import filedialog
from customtkinter import *
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd


window = CTk()
window.title("Speed Alarm for Modems")
window.geometry("700x500")

checkmarks = {
    'TX': IntVar(value=1),
    'RX': IntVar(value=1)
}

mapping = {
    'QPSK': 44,
    '16QAM': 90,
    '32QAM': 112,
    '64QAM': 135,
    '128QAM': 158,
    '256QAM': 181,
    '512QAM': 202,
    '1024QAM': 222,
    '2048QAM': 246
}

outputs = {str(i): {} for i in range(1, 13)}
times = {}
titles = {}
modems = []


def choose_file():
    global filename 
    filename = filedialog.askopenfilename(
        initialdir="/", title="Select a File", filetypes=(("All files", "*.*"), ("Text files", "*.txt*")))

def on_xlims_change(event_ax):
    xlims = event_ax.get_xlim()
    start, end = mdates.num2date(xlims[0]), mdates.num2date(xlims[1])
    visible_data = data[(data.index >= start) & (data.index <= end)]
    
    # Assuming you have a function to calculate downtime for visible data
    # You might need to adjust this to calculate separately for each modem if needed
    threshold_value = int(threshold.get())
    downtime = calculate_downtime_for_visible_data(visible_data, threshold_value)
    ax.title.set_text(
                titles[temp1]+"     "+"Total time under "+threshold.get()+" Mb/s: "+str(downtime)+" seconds")
def calculate_downtime_for_visible_data(visible_data, threshold):
    below_threshold = visible_data < threshold
    all_below_threshold = below_threshold.all(axis=1)
    
    down_time = 0
    in_downtime = False
    last_time = None
    
    for time, is_below in all_below_threshold.iteritems():
        if is_below:
            if not in_downtime:
                # Downtime starts
                in_downtime = True
                last_time = time
            # If already in downtime, continue without doing anything
        else:
            if in_downtime:
                # Downtime ends, calculate duration
                down_time += (time - last_time).total_seconds()
                in_downtime = False
                # No need to update last_time here since we're out of downtime

    # If ended while still in downtime, add the duration till the last data point
    if in_downtime:
        down_time += (visible_data.index[-1] - last_time).total_seconds()
    
    return down_time

def plot_graph(ax, y_data, total_data, modem_data):
    timestamps = pd.to_datetime(total_data[0])  # Convert your time data to DateTime
    global data
    data = pd.DataFrame({
        'Modem1_Speed': y_data[0],
        'Modem2_Speed': y_data[1],
        'Modem3_Speed': y_data[2] if len(y_data) > 2 else np.nan,  # Example for 3 modems
    }, index=timestamps)
    temp1, temp2, temp3 = '', '', ''
    temp1 = modem_data[0]
    temp2 = modem_data[1]
    temp3 = ""
    if len(modem_data) > 2:
        temp3 = modem_data[2]
    if len(y_data) > 0 and len(total_data[1]) > 0:
        locator = mdates.AutoDateLocator()
        ax.title.set_text(
                titles[temp1]+"     "+"Total time under "+threshold.get()+" Mb/s: "+str(total_data[2])+" seconds")
        ax.set_facecolor('#cccccc')
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
        ax.plot(total_data[0], y_data[0][0], label="Modem "+temp1+" Speed")
        ax.plot(total_data[0], y_data[1], label="Modem "+temp2+" Speed")
        if temp3 != '':
            ax.plot(total_data[0], y_data[2], label="Modem "+temp3+" Speed")
        ax.plot(total_data[0], y_data[1], label="Total Speed")
        ax.set_alpha(0.5)
        ax.legend(loc="lower right")
        ax.set_ylim(0, max(y_data[1])+50)
        ax.grid(True)
        ax.set_xlabel('Time')
        ax.set_ylabel('Mb/s')
        ax.callbacks.connect('xlim_changed', on_xlims_change)

def create_graph(m):
    print(times)
    times_1 = np.array(times[m[0]])
    times_2 = np.array(times[m[1]])
    times_3 = np.array([])
    if len(m) > 2:
        times_3 = np.array(times[m[2]])
    sum_times = np.concatenate((times_1, times_2, times_3), axis=None)
    sum_times = np.sort(sum_times)
    sum_times = np.unique(sum_times)
    # do a for loop to add all port 1
    speed_1, speed_2 = [], []
    for t in sum_times:
        if t in outputs[m[0]]:
            speed_1.append(outputs[m[0]][t])
        else:
            if len(speed_1) > 0:
                speed_1.append(speed_1[-1])
            else:
                speed_1.append(max(outputs[m[0]].values()))
        if t in outputs[m[1]]:
            speed_2.append(outputs[m[1]][t])
        else:
            if len(speed_2) > 0:
                speed_2.append(speed_2[-1])
            else:
                speed_2.append(max(outputs[m[1]].values()))

    total_speed = [x + y for x, y in zip(speed_1, speed_2)]
    speed_3 = []

    if len(m) > 2:

        for t in sum_times:

            if t in outputs[m[2]]:
                speed_3.append(outputs[m[2]][t])
            else:
                if len(speed_3) > 0:
                    speed_3.append(speed_3[-1])
                else:
                    speed_3.append(max(outputs[m[2]].values()))
        total_speed = [x + y for x, y in zip(total_speed, speed_3)]
    # print(total_speed)
    # get downtime

    totalx = []
    totaly = []
    y1, y2, y3 = [], [], []
    for i in range(len(sum_times)):
        if i > 0:
            totalx.append(sum_times[i])
            totaly.append(totaly[-1])
            y1.append(y1[-1])
            y2.append(y2[-1])
            if len(m)>2:
                y3.append(y3[-1])
        totalx.append(sum_times[i])
        totaly.append(total_speed[i])
        y1.append(speed_1[i])
        y2.append(speed_2[i])
        if len(m)>2:
            y3.append(speed_3[i])

    down_time = 0
    for i in range(1, len(totaly)):
        if totaly[i] < int(threshold.get()) and totaly[i-1] < int(threshold.get()) and totalx[i] != totalx[i-1]:
            print('time interval caught: ', str(totalx[i-1]), str(totalx[i]))
            print('down time', down_time, 'plus', str(
                (totalx[i]-totalx[i-1]).total_seconds()))
            down_time += (totalx[i]-totalx[i-1]).total_seconds()
    return [y1, y2, y3], [totalx, totaly, down_time]

def start_analysis():
    global outputs, times, titles
    outputs = {str(i): {} for i in range(1, 13)}
    times = {}
    try:
        month_val = month.get()
        year_val = year.get()
        with open(filename) as f:
            for line in f.read().splitlines():
                line = line.split(",")
                event_time = line[1]
                date_time_obj = datetime.strptime(event_time, '%Y/%m/%d %H:%M:%S')
                modulation = line[9]
                slot_num = line[5]
                if line[10].strip() in mapping and len(slot_num) == 6 and date_time_obj.month == int(month_val) and date_time_obj.year == int(year_val) and ((checkmarks['TX'].get() == 1 and modulation == "TX Modulation") or (checkmarks['RX'].get() == 1 and modulation == "RX Modulation")):
                    print(slot_num[5], 'confirmed')
                    speed = mapping[line[10].strip()]
                    if "0" in slot_num:
                        titles[slot_num[5]] = line[8]
                        if slot_num[5] in times:
                            times[slot_num[5]].append(date_time_obj)
                        else:
                            times[slot_num[5]] = [date_time_obj]
                        outputs[slot_num[5]][date_time_obj] = speed
                    else:
                        titles[slot_num[4:6]] = line[8]
                        if slot_num[4:6] in times:
                            times[slot_num[4:6]].append(date_time_obj)
                        else:
                            times[slot_num[4:6]] = [date_time_obj]
                        outputs[slot_num[4:6]][date_time_obj] = speed            
    except:
        print("Error Occured, try again!")
        return
    # sorting outputs of all ports
    for k in outputs.keys():
        outputs[k] = {i: outputs[k][i] for i in sorted(list(outputs[k].keys()))}
    fig, axs = plt.subplots(3, figsize=(12, 12))
    for i,m in enumerate(modems):
        modem_data = m.get().split(",")
        if len(m) > 0:
            y_data,total_data = create_graph(modem_data)
            plot_graph(axs[i], y_data, total_data, modem_data)
            
    for l in fig.gca().lines:
        l.set_alpha(.7)
    plt.subplots_adjust(left=0.05, bottom=0.06, right=0.95,
                        top=0.95, wspace=0.2, hspace=0.2)
    plt.show()

greeting = CTkLabel(window, text="Speed Alarm Graphs and Summary for Modems")
greeting.place(relx=0.5, rely=0.1, anchor=CENTER)

file_button = CTkButton(window, text="Choose your Event Log file", command=choose_file,
                        fg_color="#119149", hover_color="#45ba78")
file_button.place(relx=0.5, rely=0.2, anchor=CENTER)
month = CTkEntry(master=window, placeholder_text="Enter a month", width=120, height=25, border_width=2, corner_radius=10)
month.place(relx=0.5, rely=0.3, anchor=CENTER)
year = CTkEntry(master=window, placeholder_text="Enter a year", width=120, height=25, border_width=2, corner_radius=10)
year.place(relx=0.5, rely=0.4, anchor=CENTER)

tx = CTkCheckBox(master=window, text="TX", variable=checkmarks['TX'])
tx.place(relx=0.4, rely=0.5, anchor=CENTER)

rx = CTkCheckBox(master=window, text="RX", variable=checkmarks['RX'])
rx.place(relx=0.6, rely=0.5, anchor=CENTER)

for i in range(3):
    glabel = CTkLabel(window, text="Graph "+str(i+1)+" Modems: ")
    glabel.place(relx=0.3, rely=0.6+(i*0.1), anchor=CENTER)
    m_entry = CTkEntry(master=window, placeholder_text="Enter modems (seperated by commas)", width=120, height=25, border_width=2, corner_radius=10)
    m_entry.place(relx=0.5, rely=0.6+(i*0.1), anchor=CENTER)
    modems.append(m_entry)

threshold = CTkEntry(master=window, placeholder_text="Enter threshold", width=120, height=25, border_width=2, corner_radius=10)
threshold.place(relx=0.5, rely=0.9, anchor=CENTER)

load_button = CTkButton(window, text="Start", command=start_analysis,
                        fg_color="#119149", hover_color="#45ba78")
load_button.place(relx=0.5, rely=0.97, anchor=CENTER)

window.mainloop()
