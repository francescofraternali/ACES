'''
Reward Policies for Pible Simulation
'''
import numpy as np
import datetime
import time
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pickle
import random

# Pible sensor nodes main parameters! IMP: do not modify!!!!
I_sleep = 0.0000032; I_BLE_Sens_1 = 0.000210; Time_BLE_Sens_1 = 6.5
V_Solar_200lux = 1.5; I_Solar_200lux = 0.000031;  # It was 1.5
#V_Solar_200lux = 0.75; I_Solar_200lux = 0.0000155;  # It was 1.5
SC_Real_begin = 4; SC_Real_min = 2.1; SC_Real_max = 5.5; SC_size = 1
SC_norm_min_die = 3; SC_norm_max = 10; SC_norm_min = 0;
Light_max = 10; Light_min = 0; Light_Real_max = 2000; Light_Real_min = 0;

class Env_Rew_Pol_Sim:
    def __init__(self, start_day, end_day):
        #Settings Env Variable
        self.Light_List = []
        for i in range(0, Light_Real_max + 200, 200):
            self.Light_List.append(i)

        with open("ID.txt", 'r') as f:
            cont = f.read()
            cont_split = cont.split(',')
            self.info = cont_split[6]
            self.input_data = cont_split[2]

        with open(self.input_data) as f:
            self.content = f.readlines()
            # you may also want to remove whitespace characters like `\n` at the end of each line
        self.content = [x.strip() for x in self.content]

        splitted = self.content[0].split("|")
        self.file_begin_time = datetime.datetime.strptime(splitted[0], '%m/%d/%y %H:%M:%S')
        week_day = datetime.datetime.strptime(splitted[0], '%m/%d/%y %H:%M:%S').strftime('%a')
        if week_day == "Sat" or week_day == "Sun":
            self.week = 0
        else:
            self.week = 1

        self.start_day = start_day
        self.starting_time = self.file_begin_time + datetime.timedelta(0, (start_day/10)*24*60*60)
        self.curr_time = self.starting_time
        self.end_light_time = self.file_begin_time + datetime.timedelta(0, ((end_day/10)*24*60*60))
        print("Start date: ", self.curr_time)
        print("End date: ", self.end_light_time)
        time.sleep(5)

        self.SC_Real = SC_Real_begin; self.SC_norm_max = 10; self.SC_norm_min = 0
        self.best_reward = 0;
        self.perf = 2
        self.time_temp = 900; # State transition, take decision every 15 min
        self.Light_count = 0

        self.Tot_Reward = []; self.Tot_Episodes = []; self.Avg_Reward = []
        self.Light_hist = []; self.Action_hist = []; self.reward_hist = []; self.Time_hist = []; self.perf_hist = []; self.SC_Real_hist = []; self.SC_norm_hist = []

    def Init(self, diction_feat, episode):
        # initial observations
        self.end_time = self.curr_time + datetime.timedelta(0, (24*60*60))

        self.reward = 0; self.R = 0; self.done = False;

        splitted = self.content[self.Light_count].split("|")
        if self.Light_count == 0:
            found = 0
            for i in range(0,len(self.content)):
                splitted = self.content[i].split("|")
                self.check_time = datetime.datetime.strptime(splitted[0], '%m/%d/%y %H:%M:%S')
                #print self.check_time
                if self.check_time == self.starting_time:
                    self.Light_count = i
                    found = 1
                    break
            if found == 0:
                print("Data not Found, problem with Dates")
                quit()

        Date = splitted[0].split(" ")
        Time = Date[1].split(":")
        time_h = int(Time[0])
        time_m = int(Time[1])
        #check_time = datetime.datetime.strptime(Date[1], '%H:%M:%S')
        self.Light_Pure = int(splitted[8])
        if time_h == self.curr_time.hour and time_m == self.curr_time.minute:
            self.Light_Pure = min(self.Light_List, key=lambda x:abs(x-self.Light_Pure))
            self.Light = (((self.Light_Pure - Light_Real_min) * (Light_max - Light_min)) / (Light_Real_max - Light_Real_min)) + Light_min
            self.Light_count += 1
        else:
            print("Light Time Error Init")
            quit()

        if episode == 1000: # Randomly regenerate scupercapacitor voltage
            self.SC_Real = random.choice([3,3.5,4,4.5,5])

        self.SC_Real, self.SC_norm = calc_energy_prod_consu(self.time_temp, self.SC_Real, self.Light, self.perf)

        stuff = []
        for i in range(len(diction_feat)):
            tocheck = diction_feat[i]
            feature = checker(tocheck, self.SC_norm, self.SC_Real, self.Light, self.week)
            stuff.append(feature)

        if len(diction_feat) == 1:
            s = np.array([stuff[0]]); s_ = np.array([stuff[0]])
        elif len(diction_feat) == 2:
            s = np.array([stuff[0], stuff[1]]); s_ = np.array([stuff[0], stuff[1]])
        elif len(diction_feat) == 3:
            s = np.array([stuff[0], stuff[1], stuff[2]]); s_ = np.array([stuff[0], stuff[1], stuff[2]])
        elif len(diction_feat) == 4:
            s = np.array([stuff[0], stuff[1], stuff[2], stuff[3]]); s_ = np.array([stuff[0], stuff[1], stuff[2], stuff[3]])
        else:
            print("Dictionary Feature Error")
            exit()

        return s, s_

    def Envi(self, action, diction_feat, s_):

        # Reward Based on Action and Environment
        self.reward, self.perf_next = rew_func(action, self.SC_norm, self.perf, self.SC_norm_min)
        #reward, perf_next = rp.simple_light_rew(action, Light, perf)

        self.time_temp = 900 # State Transition every 15 min

        # Environment starts here
        self.curr_time_next = self.curr_time + datetime.timedelta(0, self.time_temp)
        date_string = self.curr_time_next.strftime('%m/%d/%y')
        week_day = datetime.datetime.strptime(date_string, '%m/%d/%y').strftime('%a')
        if week_day == "Sat" or week_day == "Sun":
            self.week = 0
        else:
            self.week = 1

        # Environment changes based on the action taken, here I Calculate Next Light intensity and Occupancy
        splitted = self.content[self.Light_count].split("|")
        Date = splitted[0].split(" ")
        Time = Date[1].split(":")
        time_h = int(Time[0])
        time_m = int(Time[1])
        self.Light_Pure = int(splitted[8])

        if time_h == self.curr_time_next.hour and time_m == self.curr_time_next.minute:
            self.Light_Pure_List = min(self.Light_List, key=lambda x:abs(x-self.Light_Pure))
            self.Light_next = (((self.Light_Pure_List - Light_Real_min) * (Light_max - Light_min)) / (Light_Real_max - Light_Real_min)) + Light_min
            self.Light_count += 1
            if self.curr_time >= self.end_time:
                self.curr_time_next = self.curr_time + datetime.timedelta(0, self.time_temp)
                self.Light_count -= 1
                #print("Day Over")
                self.done = True
                if self.curr_time >= self.end_light_time:
                    self.curr_time = self.starting_time + datetime.timedelta(0, 24*60*60)
                    self.curr_time_next = self.curr_time
                    self.Light_count = 0
                    #print("Light is Over")
        else:
            print(self.curr_time, self.curr_time_next)
            print("Light Time Error")
            quit()

        # Calculate Energy Produced and Consumed Based on the action taken
        self.SC_Real_next, self.SC_norm_next = calc_energy_prod_consu(self.time_temp, self.SC_Real, self.Light, self.perf)

        self.R += self.reward

        for i in range(len(diction_feat)):
            tocheck = diction_feat[i]
            feature = checker(tocheck, self.SC_norm_next, self.SC_Real_next, self.Light_next, self.week)
            s_[i] = feature

        return self.reward, self.done, s_

    def Update_s(self, action, diction_feat, s, episode):

        self.Light_hist.append(self.Light); self.Action_hist.append(action); self.reward_hist.append(self.reward); self.Time_hist.append(self.curr_time); self.perf_hist.append(self.perf); self.SC_Real_hist.append(self.SC_Real); self.SC_norm_hist.append(self.SC_norm);

        # swap observation
        for i in range(len(diction_feat)):
            tocheck = diction_feat[i]
            feature = checker(tocheck, self.SC_norm_next, self.SC_Real_next, self.Light_next, self.week)
            s[i] = feature
        #s = s_;
        self.perf = self.perf_next;
        self.Light = self.Light_next;
        self.curr_time = self.curr_time_next;
        self.SC_norm = self.SC_norm_next; self.SC_Real = self.SC_Real_next;

        return s

    def printing(self, Text, episode, tot_episodes, epsilon, write_to_file):

        self.Tot_Reward.append(self.R); self.Tot_Episodes.append(episode); self.Avg_Reward.append(sum(self.Tot_Reward)/len(self.Tot_Reward))
        print(Text + ", Epis: " + str(episode) + "/" + str(tot_episodes) + ", Rew: " + str(self.R) + ", Max_R: " + str(self.best_reward) + ", Avg_R: " + str(sum(self.Tot_Reward)/len(self.Tot_Reward)) + ", Ep: " + str(epsilon))

        if write_to_file:
            with open('Final_Results.txt', 'a') as myfile:
                myfile.write("Results " + str(Text) + ": Epis: " + str(episode) + ", Rew: " + str(self.R) + ", Max_R: " + str(self.best_reward) + ", Avg_R: " + str(sum(self.Tot_Reward)/len(self.Tot_Reward)) + ", Ep: " + str(epsilon) + "\n")
            myfile.close()
            plot_graph(self.Time_hist, self.Light_hist, self.Action_hist, self.reward_hist, self.perf_hist, self.SC_Real_hist, self.SC_norm_hist, Text, self.best_reward, episode, self.R)

def rew_func(action, SC_norm, perf, SC_norm_min): # not finished yet
    perf = action
    reward = perf
    if SC_norm <= SC_norm_min_die:
        reward = - 300

    return reward, perf


def calc_energy_prod_consu(time_temp, SC_Real, Light, perf):

    if perf == 3:
        effect = 60
    elif perf == 2:
        effect = 15
    elif perf == 1:
        effect = 3
    else:
        effect = 1

    Energy_Rem = SC_Real * SC_Real * 0.5 * SC_size

    #print "SC Real Begninning: " + str(SC_Real)
    if SC_Real <= SC_Real_min:
        Energy_Prod = time_temp * V_Solar_200lux * I_Solar_200lux * Light
        Energy_Used = 0
    else:
        Energy_Used = ((time_temp - (Time_BLE_Sens_1 * effect)) * SC_Real * I_sleep) + (Time_BLE_Sens_1 * effect * SC_Real * I_BLE_Sens_1)
        Energy_Prod = time_temp * V_Solar_200lux * I_Solar_200lux * Light

    Energy_Rem = Energy_Rem - Energy_Used + Energy_Prod

    if Energy_Rem < 0:
        Energy_Rem = 0

    SC_Real = np.sqrt((2*Energy_Rem)/SC_size)

    if SC_Real > SC_Real_max:
        SC_Real = SC_Real_max

    if SC_Real < SC_Real_min:
        SC_Real = SC_Real_min

    SC_norm = round((((SC_Real - SC_Real_min) * (SC_norm_max - SC_norm_min)) / (SC_Real_max - SC_Real_min)) + SC_norm_min)

    return SC_Real, SC_norm

def plot_graph(Time, Light, Action, reward, perf, SC_Real, SC_norm, Text, best_reward, tot_episodes, R):
    #Start Plotting
    plt.figure(1)
    ax1 = plt.subplot(411)
    #plt.title(('Transmitting every {0} sec, PIR {1} ({2} events). Tot reward: {3}').format('60', using_PIR, PIR_events, tot_rew))
    plt.title(Text + ", Rew: " + str(R), fontsize = 17)
    plt.plot(Time, Light, 'b-', label = 'Light', markersize = 15)
    plt.ylabel('Light\n[lux]', fontsize=15)
    ax1.set_xticklabels([])
    plt.grid(True)
    ax2 = plt.subplot(412)
    plt.plot(Time, SC_norm, 'k.', label = 'Detected', markersize = 15)
    plt.ylabel('SC\nNorm\n[num]', fontsize=15)
    #plt.xlabel('Time [h]', fontsize=20)
    #plt.legend(loc=1, prop={'size': 9})
    ax2.set_xticklabels([])
    plt.grid(True)
    ax3 = plt.subplot(413)
    plt.plot(Time, SC_Real, 'r.', label = 'SC Voltage', markersize = 15)
    plt.ylabel('SC [V]\nVolt', fontsize=15)
    #plt.legend(loc=9, prop={'size': 10})
    plt.ylim(2.2,5.6)
    ax3.set_xticklabels([])
    plt.grid(True)
    ax4 = plt.subplot(414)
    plt.plot(Time, Action, 'y.', label = 'PIR_OnOff', markersize = 15)
    plt.ylabel('PIR\nAction\n[num]', fontsize=15)
    plt.xlabel('Time [h]', fontsize=20)
    plt.ylim(0)
    plt.grid(True)

    ax4.tick_params(axis='both', which='major', labelsize=12)

    xfmt = mdates.DateFormatter('%m/%d %H')
    ax4.xaxis.set_major_formatter(xfmt)
    plt.grid(True)
    #plt.savefig('Graph.png', bbox_inches='tight')
    plt.show()
    plt.close()

def checker(tc, SC_norm, SC_real, Light, week):
    if tc == "SC_norm":
        return SC_norm
    elif tc == "Light":
        return Light
    elif tc == "SC_temp":
        return SC_temp
    elif tc == "SC_real":
        return SC_real
    elif tc == "week":
        return week

    else:
        print("Checher Error")
        quit()
        return "error"
