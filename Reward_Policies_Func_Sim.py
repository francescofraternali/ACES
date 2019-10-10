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
#from Light_Env import calc_light_occup_real
SC_Volt_min = 2.3; SC_Volt_max = 5.4; SC_size = 1.5

I_Wake_up_Advertise = 0.00006; Time_Wake_up_Advertise = 11
I_BLE_Comm = 0.00025; Time_BLE_Comm = 4
I_BLE_Sens_1= ((I_Wake_up_Advertise * Time_Wake_up_Advertise) + (I_BLE_Comm * Time_BLE_Comm))/(Time_Wake_up_Advertise + Time_BLE_Comm)
Time_BLE_Sens_1 = Time_Wake_up_Advertise + Time_BLE_Comm

I_sleep = 0.0000032;
using_PIR = 1
I_PIR_detect = 0.000102; PIR_detect_time = 2.5
if using_PIR == 1:
    I_sleep = 0.0000055

V_Solar_200lux = 1.5; I_Solar_200lux = 0.000031;  # It was 1.5
#V_Solar_200lux = 0.75; I_Solar_200lux = 0.0000155;  # It was 1.5
SC_Real_begin = 4; SC_Real_min = 2.3; SC_Real_max = 5.4;
SC_norm_min_die = 3; SC_norm_max = 10; SC_norm_min = 0;
Light_max = 10; Light_min = 0; Light_Real_max = 2000; Light_Real_min = 0;

class Env_Rew_Pol_Sim:
    def __init__(self, Light_Input):
        #Settings Env Variable
        #self.Start_Real_Time = datetime.datetime.now().strftime('%m-%d %H:%M')
        self.Light_List = []
        for i in range(0, Light_Real_max + 200, 200):
            self.Light_List.append(i)


        with open(Light_Input) as f:
            self.content = f.readlines() # you may also want to remove whitespace characters like `\n` at the end of each line
        self.content = [x.strip() for x in self.content]
        # you may also want to remove whitespace characters like `\n` at the end of each line
        Splitted = self.content[0].split("|")
        #Date = Splitted[0].split(" ")
        #Split_Date = Date[0].split("/")
        #self.Year = int(Split_Date[2])
        #self.Day = int(Split_Date[1])
        #self.Month = int(Split_Date[0])
        #Time = Date[1].split(":")
        #self.curr_time_h = int(Time[0])
        #self.curr_time_m = int(Time[1])
        #self.Start_Real_Time = datetime.datetime.now()
        #self.File_Begin_time = File_Begin_Time
        self.File_Begin_time = datetime.datetime.strptime(Splitted[0], '%m/%d/%y %H:%M:%S')
        week_day = datetime.datetime.strptime(Splitted[0], '%m/%d/%y %H:%M:%S').strftime('%a')
        if week_day == "Sat" or week_day == "Sun":
            self.week = 0
        else:
            self.week = 1
        #self.Starting_time = datetime.datetime(self.Year,self.Month,self.Day,self.curr_time_h,self.curr_time_m,00)
        #self.Ending_time = datetime.datetime(2018,1,2,6,00,00)
        #self.start_day = start_day
        #self.Starting_time = self.File_Begin_time + datetime.timedelta(0, (start_day/10)*24*60*60)
        self.Starting_time = datetime.datetime.strptime(Splitted[0], '%m/%d/%y %H:%M:%S')
        self.sim_curr_time = self.Starting_time
        #self.End_Light_time = self.File_Begin_time + datetime.timedelta(0, ((end_day/10)*24*60*60))
        print("Starting Simulation from: " + str(self.sim_curr_time))
        #print self.End_Light_time
        #quit()
        time.sleep(1)
        self.SC_Real = SC_Real_begin
        self.best_reward = 0;
        self.stop = 0
        self.perf = 1
        self.time_temp = 4;
        self.Light_count = 0


        self.Light_Best = []; self.SC_Real_Best = []; self.perf_Best = []; self.Time_Best = []; self.Action_Best = []; self.r_Best = []; self.cnt_Best = []; self.SC_Best_norm_hist = []; self.SC_Feed_Best = []; self.Light_Feed_Best = [];
        self.Tot_Reward = []; self.Tot_Episodes = []; self.Avg_Reward = []
        self.Light_hist = []; self.Action_hist = []; self.reward_hist = []; self.Time_hist = []; self.perf_hist = []; self.SC_Real_hist = []; self.SC_norm_hist = [];  self.data_out_hist = []
        self.Action_hist_dc = []; self.reward_hist_dc = []; self.perf_hist_dc = []; self.SC_Real_hist_dc = []; self.SC_norm_hist_dc = []; self.data_out_hist_dc = []

    def Init(self, diction_feat, granularity, episode):
        # initial observation
        #self.curr_time = self.Starting_time
        #self.curr_time_h = self.curr_time.hour
        #self.curr_time_m = self.curr_time.minute
        self.end_time = self.sim_curr_time + datetime.timedelta(0, (24*60*60))

        self.reward = 0; self.R = 0; self.done = False; self.data_out = 0;
        self.R_dc = 0; self.reward_dc = 0; self.data_out_dc = 0


        Splitted = self.content[self.Light_count].split("|")

        datetime_read = datetime.datetime.strptime(Splitted[0], '%m/%d/%y %H:%M:%S')

        self.PIR = int(Splitted[6])
        self.Light_Pure = int(Splitted[8])
        #print time_h, time_m
        #print self.curr_time_h, self.curr_time_m
        #print self.Light_count
        #print("Start")
        #print self.curr_time
        #print self.content[self.Light_count]
        #time.sleep(3)
        #print(str(self.sim_curr_time) + " sim time")
        #print(str(datetime_read) + " read init")
        if datetime_read.hour == self.sim_curr_time.hour and datetime_read.minute == self.sim_curr_time.minute:
            self.Light_Pure = min(self.Light_List, key=lambda x:abs(x-self.Light_Pure))
            self.Light = (((self.Light_Pure - Light_Real_min) * (Light_max - Light_min)) / (Light_Real_max - Light_Real_min)) + Light_min
            self.Light_count += 1
        else:
            print("Light Time Error Init")
            quit()

        if episode % 200 == 0:
            self.SC_Real = random.choice([2,2.5,3,3.5,4,4.5,5,5.4])

        self.SC_Real, self.SC_norm = calc_energy_prod_consu(self.time_temp, self.SC_Real, self.Light, granularity, self.perf, self.PIR)
        #self.SC_real = round(self.SC_temp,1)

        stuff = []
        for i in range(len(diction_feat)):
            tocheck = diction_feat[i]
            feature = checker(tocheck, self.SC_norm, self.SC_Real, self.Light, self.sim_curr_time.hour, self.sim_curr_time.minute, self.week)
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

#        self.SC_norm_dc = self.SC_norm; self.SC_Real_dc = self.SC_Real; self.perf_dc = self.perf
#        self.SC_norm_next_dc = 0; self.SC_Real_next_dc = 0; self.perf_next_dc = 0
        return s, s_

    def Envi(self, action, tot_action, diction_feat, s_, granularity):

        # Reward Based on Action and Environment
        self.reward, self.perf_next, self.data_out = rew_func(action, tot_action, self.SC_norm, self.perf, SC_norm_min, self.data_out)
        #self.reward_dc, self.perf_next_dc, self.data_out_dc = simple_barath_sending_and_dying_rew(action_dc, tot_action, self.SC_norm_dc, self.perf_dc, SC_norm_min, granul, self.data_out_dc)
        #reward, perf_next = rp.simple_light_rew(action, Light, perf)

        # Adjust Performance and Time
        self.time_temp = granularity
        #self.perf_next, self.time_temp = adjust_perf(self.perf_next, granul)  #time_temp = 600
        #self.perf_next_dc, self.time_temp = adjust_perf(self.perf_next_dc, granul)  #time_temp = 600

        # Environment starts here
        # Adjust Environment Time
        self.sim_curr_time_next = self.sim_curr_time + datetime.timedelta(0, self.time_temp)
        date_string = self.sim_curr_time_next.strftime('%m/%d/%y')
        week_day = datetime.datetime.strptime(date_string, '%m/%d/%y').strftime('%a')
        if week_day == "Sat" or week_day == "Sun":
            self.week = 0
        else:
            self.week = 1

        # Environment changes based on the action taken, here I Calculate Next Light intensity and Occupancy
        #self.Light_next = calc_light_occup(self.curr_time_h_next, self.curr_time_m_next, self.info)
        #print self.content[self.Light_count]
        Splitted = self.content[self.Light_count].split("|")
        datetime_read = datetime.datetime.strptime(Splitted[0], '%m/%d/%y %H:%M:%S')
        #Date = Splitted[0].split(" ")
        #Time = Date[1].split(":")
        #time_h = int(Time[0])
        #time_m = int(Time[1])
        #check_time = datetime.datetime.strptime(Date[1], '%H:%M:%S')
        self.PIR = int(Splitted[6])
        self.Light_Pure = int(Splitted[8])
        #print self.Light_count
        #print self.content[self.Light_count]
        #print(str(datetime_read),self.curr_time_next)
        #print self.end_time
        #print time_h, time_m
        #print self.curr_time_h_next, self.curr_time_m_next
        #print(str(self.sim_curr_time_next) + " sim time")
        #print(str(datetime_read) + "read time")
        if datetime_read.hour == self.sim_curr_time_next.hour and datetime_read.minute == self.sim_curr_time_next.minute:
            self.Light_Pure_List = min(self.Light_List, key=lambda x:abs(x-self.Light_Pure))
            self.Light_next = (((self.Light_Pure_List - Light_Real_min) * (Light_max - Light_min)) / (Light_Real_max - Light_Real_min)) + Light_min
            self.Light_count += 1
            if self.sim_curr_time >= self.end_time or self.Light_count == len(self.content):
                self.sim_curr_time_next = self.sim_curr_time_next + datetime.timedelta(0, self.time_temp)
                #print self.curr_time
                #print self.curr_time_next
                #print datetime_read
                #print self.content[self.Light_count]
                #self.Light_count -= 1
                #print("Day Over")
                self.done = True
                if self.Light_count == len(self.content):
                #if self.curr_time >= self.End_Light_time:
                    #self.curr_time = self.File_Begin_time
                    #self.curr_time_next = self.curr_time
                    #if self.Light_count == len(self.content):
                    self.Light_count = 0
                    #self.done = True
                    #print self.curr_time
                    #print self.curr_time_next
                    #print self.end_time
                    #print "End", self.End_Light_time
                    #print("Light is Over")
                    #quit()
        else:
            print("Light Time Error")
            quit()

        #print Splitted[0], self.Light_Pure, self.Light_Pure_List, self.Light_next
        #time.sleep(2)
        # Calculate Energy Produced and Consumed Based on the action taken
        self.SC_Real_next, self.SC_norm_next = calc_energy_prod_consu(self.time_temp, self.SC_Real, self.Light, granularity, self.perf, self.PIR)
        #self.SC_Real_next_dc, self.SC_norm_next_dc = calc_energy_prod_consu(self.time_temp, self.SC_Real_dc, self.Light, granularity, self.perf_dc, granul)
        #self.SC_Real_next = round(self.SC_Real_next,1)

        self.R += self.reward
        #self.R_dc += self.reward_dc

        #if cnt >= cnt_max:
        #if self.curr_time >= self.end_time:
        #    #self.end_time = self.curr_time + datetime.timedelta(0, 24*60*60)
        #    self.curr_time = self.Starting_time + datetime.timedelta(0, (self.start_day/10)*24*60*60)
        #    self.curr_time_next = self.curr_time #+ datetime.timedelta(0, self.time_temp)
        #    #self.curr_time_next = self.curr_time_next #+ datetime.timedelta(0, self.time_temp)
        #    #self.curr_time_next = self. + datetime.timedelta(0, self.time_temp)
        #    print("Day Over")
        #    #print self.curr_time
        #    #print self.curr_time_next
        #    self.done = True

        for i in range(len(diction_feat)):
            tocheck = diction_feat[i]
            feature = checker(tocheck, self.SC_norm_next, self.SC_Real_next, self.Light_next, self.sim_curr_time_next.hour, self.sim_curr_time_next.minute, self.week)
            s_[i] = feature

        return self.reward, self.done, s_

    def Update_s(self, action, diction_feat, s, episode, save_rate):

        if episode % save_rate == 0:
            # Append Data
            self.Light_hist.append(self.Light); self.Action_hist.append(action); self.reward_hist.append(self.reward); self.Time_hist.append(self.sim_curr_time); self.perf_hist.append(self.perf); self.SC_Real_hist.append(self.SC_Real); self.SC_norm_hist.append(self.SC_norm); self.data_out_hist.append(self.data_out)

            #self.Action_hist_dc.append(action_dc); self.reward_hist_dc.append(self.reward_dc); self.perf_hist_dc.append(self.perf_dc); self.SC_Real_hist_dc.append(self.SC_Real_dc); self.SC_norm_hist_dc.append(self.SC_norm_dc); self.data_out_hist_dc.append(self.data_out_dc)

        # swap observation
        for i in range(len(diction_feat)):
            tocheck = diction_feat[i]
            feature = checker(tocheck, self.SC_norm_next, self.SC_Real_next, self.Light_next, self.sim_curr_time_next.hour, self.sim_curr_time_next.minute, self.week)
            s[i] = feature
        #s = s_;
        self.perf = self.perf_next;
        self.Light = self.Light_next;
        self.sim_curr_time = self.sim_curr_time_next;
        self.SC_norm = self.SC_norm_next; self.SC_Real = self.SC_Real_next;

        #self.SC_norm_dc = self.SC_norm_next_dc; self.SC_Real_dc = self.SC_Real_next_dc; self.perf_dc = self.perf_next_dc;

        return s

    def printing(self, Text, episode, tot_episodes, epsilon, write_to_file):

        #plot_hist(self.Time_hist, self.Light_hist, self.Action_hist, self.reward_hist, self.perf_hist, self.SC_Real_hist, self.SC_norm_hist, Text, self.best_reward, episode)
        #self.Curr_Real_Time = datetime.datetime.now()
        #Time_Passed = self.Curr_Real_Time - self.Start_Real_Time
        #if self.R < 0:
        #    self.R = 0
        if self.R > self.best_reward:
            self.best_reward = self.R

        self.Tot_Reward.append(self.R); self.Tot_Episodes.append(episode); self.Avg_Reward.append(sum(self.Tot_Reward)/len(self.Tot_Reward))
        #print(Text + ", Epis: " + str(episode) + "/" + str(tot_episodes) + ", Rew: " + str(self.R) + ", Max_R: " + str(self.best_reward) + ", Avg_R: " + str(sum(self.Tot_Reward)/len(self.Tot_Reward)) +", Calcul_Time: " + str(Time_Passed) + ", Ep: " + str(epsilon))
        print(Text + ", Epis: " + str(episode) + "/" + str(tot_episodes) + ", Rew: " + str(self.R) + ", Max_R: " + str(self.best_reward) + ", Ep: " + str(round(epsilon,4)))


        #if self.R > self.best_reward:
        #    self.best_reward = self.R
        #    self.Light_Best = self.Light_hist; self.Action_Best = self.Action_hist; self.reward_Best = self.reward_hist; self.best_reward = self.R; self.Time_Best = self.Time_hist; self.perf_Best = self.perf_hist; self.SC_Real_Best = self.SC_Real_hist
        #    self.SC_Best_norm_hist = self.SC_norm_hist;

        #    plot_best(self.Time_Best, self.Light_Best, self.Action_Best, self.reward_Best, self.perf_Best, self.SC_Real_Best, self.SC_Best_norm_hist, Text, self.best_reward, episode)
        #    plot_reward_text(self.Tot_Episodes, self.Tot_Reward, Text, self.best_reward, episode, self.Avg_Reward)
        #    with open('Saved_Data/Graph_Best_' + Text + '.pkl', 'w') as f:  # Python 3: open(..., 'wb')
        #        pickle.dump([self.Light_Best, self.Action_Best, self.reward_Best, self.best_reward, self.Time_Best, self.perf_Best, self.SC_Real_Best, self.SC_Best_norm_hist, self.Tot_Episodes, self.Tot_Reward, Text, episode], f)

    def saving(self, Text, episode, tot_episodes, epsilon, write_to_file):

        #plot_reward_text(self.Tot_Episodes, self.Tot_Reward, Text, self.best_reward, episode, self.Avg_Reward)
        with open('Saved_Data/Graph_hist_' + Text + '.pkl', 'wb') as f:  # Python 3: open(..., 'wb')
            pickle.dump([self.Light_hist, self.Action_hist, self.reward_hist, self.best_reward, self.Time_hist, self.perf_hist, self.SC_Real_hist, self.SC_norm_hist, self.Tot_Episodes, self.Tot_Reward, Text, episode, self.Action_hist_dc, self.reward_hist_dc, self.SC_Real_hist_dc, self.R_dc, self.R, self.data_out, self.data_out_dc], f, protocol=2)
        #plot_hist(self.Time_hist, self.Light_hist, self.Action_hist, self.reward_hist, self.perf_hist, self.SC_Real_hist, self.SC_norm_hist, Text, self.best_reward, episode, self.Action_hist_dc, self.reward_hist_dc, self.SC_Real_hist_dc, self.R_dc, self.R, self.data_out, self.data_out_dc)
        #with open('Saved_Data/Avg_Reward_' + Text + '.pkl', 'w') as f:  # Python 3: open(..., 'wb')
        #    pickle.dump([self.Tot_Reward, self.Tot_Episodes, self.Avg_Reward], f)

        with open('Final_Results.txt', 'a') as myfile:
            myfile.write("Results " + str(Text) + ": Epis: " + str(episode) + ", Rew: " + str(self.R) + ", Max_R: " + str(self.best_reward) + ", Avg_R: " + str(sum(self.Tot_Reward)/len(self.Tot_Reward)) + ", Ep: " + str(epsilon) + "\n")

def rew_func(action, tot_action, SC_norm, perf, SC_norm_min, data_out): # not finished yet

    perf = action

    # every time you send a data in 15mins you get 1000 points
    if perf == 3:
        reward = 3
        data_out += 60
    elif perf == 2:
        reward = 2
        data_out += 15
    elif perf == 1:
        reward = 1
        data_out += 3
    elif perf == 0:
        reward = 0
        data_out += 1


    if SC_norm <= SC_norm_min_die:
        reward = - 300
    if perf == 0 and SC_norm <= SC_norm_min_die:
        reward = - 100


    return reward, perf, data_out

#def adjust_perf(perf, granularity):

#    time_temp = granularity

#    return perf, time_temp

def calc_energy_prod_consu(time_temp, SC_Real, Light, granularity, perf, PIR):
    
    if perf ==  3:
        effect = granularity/15; effect_PIR = granularity/30
    elif perf == 2:
        effect = granularity/60; effect_PIR = granularity/60
    elif perf == 1:
        effect = granularity/300; effect_PIR = granularity/300
    else:
        effect = granularity/900; effect_PIR = granularity/900

    Energy_Rem = SC_Real * SC_Real * 0.5 * SC_size

    #print "SC Real Begninning: " + str(SC_Real)
    if SC_Real <= SC_Real_min:
        Energy_Prod = time_temp * V_Solar_200lux * I_Solar_200lux * Light
        Energy_Used = 0
        #print "here_ 1"
    else:
        if using_PIR == 1:
            effect_PIR = 0

        Energy_Used = ((time_temp - (Time_BLE_Sens_1 * effect)) * SC_Real * I_sleep) + (Time_BLE_Sens_1 * effect * SC_Real * I_BLE_Sens_1) + (PIR * I_PIR_detect * PIR_detect_time * effect_PIR)

        Energy_Prod = time_temp * V_Solar_200lux * I_Solar_200lux * Light
        #print "here_2"

    #print "Light: " + str(Light)
    #print "Ener_Produ: " + str(Energy_Prod)
    #print "Energy_Used: " + str(Energy_Used)
    #print Energy_Used
    #print "Energy_Rem First: " +str(Energy_Rem)
    Energy_Rem = Energy_Rem - Energy_Used + Energy_Prod
    #print "Energy_Rem After: " +str(Energy_Rem)

    if Energy_Rem < 0:
        Energy_Rem = 0

    SC_Real = np.sqrt((2*Energy_Rem)/SC_size)
    #print "SC Real First: " + str(SC_Real)
    #print Energy_Used

    if SC_Real > SC_Real_max:
        SC_Real = SC_Real_max

    if SC_Real < SC_Real_min:
        SC_Real = SC_Real_min


    #print "SC Real Final: " + str(SC_Real)

    SC_norm = round((((SC_Real - SC_Real_min) * (SC_norm_max - SC_norm_min)) / (SC_Real_max - SC_Real_min)) + SC_norm_min)

    return SC_Real, SC_norm

def plot_reward_text(Tot_Episodes, Tot_Reward, Text, best_reward, tot_episodes, Avg_Reward):
    #Start Plotting
    fig, ax = plt.subplots(1)
    #fig.autofmt_xdate()
    plt.plot(Tot_Episodes, Avg_Reward, 'r', label = 'Total Reward')
    #xfmt = mdates.DateFormatter('%m-%d-%y %H:%M:%S')
    #ax.xaxis.set_major_formatter(xfmt)
    ax.tick_params(axis='both', which='major', labelsize=10)
    legend = ax.legend(loc='center right', shadow=True)
    plt.legend(loc=9, prop={'size': 10})
    plt.title('Reward Trend - ' + Text + ', Best_R: ' + str(best_reward) + ', Epis: ' + str(tot_episodes), fontsize=15)
    plt.ylabel('Total Reward [num]', fontsize=15)
    plt.xlabel('Episode [num]', fontsize=20)
    ax.grid(True)
    #fig.savefig('/mnt/c/Users/Francesco/Dropbox/EH/RL/RL_MY/Images-Auto/Reward_' + Text + '.png', bbox_inches='tight')
    fig.savefig('Images-Auto/Avg_Reward_' + Text + '.png', bbox_inches='tight')
    #plt.show()
    plt.close(fig)

def plot_best(Time_Best, Light_Best, Action_Best, reward_Best, perf_Best, SC_Real_Best, SC_Best_norm_hist, Text, best_reward, tot_episodes):
    #Start Plotting
    fig, ax = plt.subplots(1)
    fig.autofmt_xdate()
    plt.plot(Time_Best, Light_Best, 'b', label = 'Light')
    #plt.plot(Time_Best, Light_Feed_Best, 'b', label = 'Light Feeded')
    plt.plot(Time_Best, Action_Best, 'y*', label = 'Action',  markersize = 15)
    plt.plot(Time_Best, reward_Best, 'k+', label = 'Reward')
    plt.plot(Time_Best, perf_Best, 'g', label = 'Performance')
    plt.plot(Time_Best, SC_Real_Best, 'r+', label = 'SC_Voltage')
    plt.plot(Time_Best, SC_Best_norm_hist, 'm^', label = 'SC_Voltage_Normalized')
    plt.plot(Time_Best, SC_Best_norm_hist, 'm')
    #plt.plot(Time_Best, SC_Feed_Best, 'c^', label = 'SC_Voltage_Feeded')
    #plt.plot(Time_Best, Occup_Best, 'c^', label = 'Occupancy')
    xfmt = mdates.DateFormatter('%m-%d-%y %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    ax.tick_params(axis='both', which='major', labelsize=10)
    legend = ax.legend(loc='center right', shadow=True)
    plt.legend(loc=9, prop={'size': 10})
    plt.title(Text + ', Best_R: ' + str(best_reward) + ', Epis: ' + str(tot_episodes), fontsize=15)
    plt.ylabel('Super Capacitor Voltage[V]', fontsize=15)
    plt.xlabel('Time[h]', fontsize=20)
    ax.grid(True)
    fig.savefig('Images-Auto/Graph_Best_' + Text + '.png', bbox_inches='tight')
    #plt.show()
    plt.close(fig)

def plot_hist(Time_Best, Light_Best, Action_Best, reward_Best, perf_Best, SC_Real_Best, SC_Best_norm_hist, Text, best_reward, tot_episodes, Action_hist_dc, reward_hist_dc, SC_Real_hist_dc, R_dc, R, data_out, data_out_dc):
    #Start Plotting
    fig, ax = plt.subplots(1)
    fig.autofmt_xdate()
    plt.plot(Time_Best, Light_Best, 'b', label = 'Light')
    #plt.plot(Time_Best, Light_Feed_Best, 'b', label = 'Light Feeded')
    plt.plot(Time_Best, Action_Best, 'y*', label = 'Action',  markersize = 15)
    plt.plot(Time_Best, reward_Best, 'k+', label = 'Reward')
    plt.plot(Time_Best, perf_Best, 'g', label = 'Performance')
    plt.plot(Time_Best, SC_Real_Best, 'r+', label = 'SC_Voltage')
    plt.plot(Time_Best, SC_Best_norm_hist, 'm^', label = 'SC_Voltage_Normalized')
    plt.plot(Time_Best, SC_Best_norm_hist, 'm')
    plt.plot(Time_Best, reward_hist_dc, 'k.', label = 'Reward DC')
    plt.plot(Time_Best, Action_hist_dc, 'g.', label = 'Action DC')
    #plt.plot(Time_Best, SC_Feed_Best, 'c^', label = 'SC_Voltage_Feeded')
    #plt.plot(Time_Best, Occup_Best, 'c^', label = 'Occupancy')
    xfmt = mdates.DateFormatter('%m-%d-%y %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    ax.tick_params(axis='both', which='major', labelsize=10)
    legend = ax.legend(loc='center right', shadow=True)
    plt.legend(loc=9, prop={'size': 10})
    plt.title(Text + ', Best_R: ' + str(best_reward) + ', Epis: ' + str(tot_episodes), fontsize=15)
    plt.ylabel('Super Capacitor Voltage[V]', fontsize=15)
    plt.xlabel('Time[h]', fontsize=20)
    ax.grid(True)
    fig.savefig('Saved_Data/Graph_hist_' + Text + '.png', bbox_inches='tight')
    #plt.show()
    plt.close(fig)


def checker(tc, SC_norm, SC_real, Light, curr_time_h, curr_time_m, week):
    if tc == "SC_norm":
        return SC_norm
    elif tc == "Light":
        return Light
    elif tc == "SC_temp":
        return SC_temp
    elif tc == "SC_real":
        return SC_real
    elif tc == "SC_feed":
        return SC_feed
    elif tc == "Light_feed":
        return Light_feed
    elif tc == "curr_time_h":
        return curr_time_h
    elif tc == "curr_time_m":
        return curr_time_m
    elif tc == "curr_time_h_feed":
        return curr_time_h_feed
    elif tc == "curr_time_m_feed":
        return curr_time_m_feed
    elif tc == "week":
        return week

    else:
        print("Checher Error")
        quit()
        return "error"
