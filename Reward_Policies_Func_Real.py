'''
Reward Policies for Pible Simulation

'''
import numpy as np
import datetime
import time
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pickle
from file_read_backwards import FileReadBackwards

SC_Real_min = 2.3; SC_Real_max = 5.4; SC_norm_max = 10; SC_norm_min = 0; SC_norm_min_die = 3;
Light_Real_min = 0; Light_Real_max= 2000; Light_max = 10; Light_min = 0


class Env_Rew_Pol_Real:
    def __init__(self):
        #Settings Env Variable
        #self.Start_Real_Time = datetime.datetime.now().strftime('%m-%d %H:%M')
        #self.Starting_time = datetime.datetime(2018,1,1,6,00,00)
        #self.Ending_time = datetime.datetime(2018,1,2,6,00,00)
        #self.Time_h_min = 0; self.Time_h_max = 24; self.Time_m_max = 60
        self.best_reward = 0; self.Perc_Best = 0
        self.perf_Pure = 0; self.perf = 0; self.reward = self.perf; self.R = 0; self.done = False; self.SC_Pure = 0; self.Light_Pure = 0; self.Light = 0; self.SC_Pure_float = 0; self.SC_norm = 0;
        self.Light_Best = []; self.SC_Pure_Best = []; self.perf_Best = []; self.Time_Best = []; self.Action_Best = []; self.reward_Best = []; self.SC_Best_norm_hist = [];
        self.Tot_Reward = []; self.Tot_Episodes = []
        self.Light_hist = []; self.Action_hist = []; self.reward_hist = []; self.Time_hist = []; self.perf_hist = []; self.SC_Pure_hist = []; self.SC_norm_hist = [];
        self.Node_Death = False
        self.Light_List = []
        for i in range(0, Light_Real_max + 200, 200):
            self.Light_List.append(i)

        self.T_m_List = []
        for i in range(0, 60, 15):
            self.T_m_List.append(i)

    def Init(self, diction_feat, granul, Input_Data):
        # initial observation
        '''
        with open(Input_Data) as f:
            self.content = f.readlines()
            # you may also want to remove whitespace characters like `\n` at the end of each line
        self.content = [x.strip() for x in self.content]
        '''

        with FileReadBackwards(Input_Data, encoding="utf-8") as frb:
            # getting lines by lines starting from the last line up
            for old in frb:
                #print(old)
                Splitted = old.strip().split("|")
                if len(Splitted) > 7 and Splitted[5].isdigit() and int(Splitted[5]) != 0:
                    break

        '''
        for i in range(1,len(self.content)):
            old = self.content[-i]
            Splitted = old.split("|")
            #print(old)
            #print(len(old.split('|')))
            if len(Splitted) > 10 and int(Splitted[5]) != 0:
                break
        '''

        #print(old)
        #print(Input_Data)
        #print(Splitted[5])
        # you may also want to remove whitespace characters like `\n` at the end of each line

        #print(Splitted)
        time = datetime.datetime.strptime(Splitted[0], '%m/%d/%y %H:%M:%S')
        self.Year = time.year
        self.Day = time.day
        self.Month = time.month
        self.curr_time_h = time.hour
        self.curr_time_m = time.minute
        self.curr_time_m = min(self.T_m_List, key=lambda x:abs(x-self.curr_time_m))
        self.curr_time = datetime.datetime(self.Year, self.Month, self.Day, self.curr_time_h, self.curr_time_m)
        week_day = datetime.datetime.strptime(Splitted[0], '%m/%d/%y %H:%M:%S').strftime('%a')
        if week_day == "Sat" or week_day == "Sun":
            self.week = 0
        else:
            self.week = 1
        self.end_time = self.curr_time + datetime.timedelta(0, 60*60*24) # I wanna stop the epidode the day later

        #self.end_time = datetime.datetime(self.Year, self.Month, self.Day, self.curr_time_h,self.curr_time_m)

        if len(Splitted) < 9 or Splitted[5] == '0':

                stuff = []
                for i in range(len(diction_feat)):
                    tocheck = diction_feat[i]
                    feature = checker(tocheck, 0, 0, 0, 0, 0, 0)
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

                return s, s_, old, 0 , 0

        Light_Pure = int(Splitted[8])
        if Light_Pure > Light_Real_max:
            Light_Pure = Light_Real_max

        # Normalize Light from 0 % 4000 to 0 % 10 with NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        self.Light_Pure = min(self.Light_List, key=lambda x:abs(x-Light_Pure))
        self.Light = (((self.Light_Pure - Light_Real_min) * (Light_max - Light_min)) / (Light_Real_max - Light_Real_min)) + Light_min

        # Normalize SC_Volt from 100 % 0 to 0 % 10
        self.SC_Pure = int(Splitted[5])
        #print self.SC_Pure
        self.SC_Pure_float = (self.SC_Pure/100.0)*5.4

        if self.SC_Pure_float > SC_Real_max:
            self.SC_Pure_float = SC_Real_max

        self.SC_norm = round((((self.SC_Pure_float - SC_Real_min) * (SC_norm_max - SC_norm_min)) / (SC_Real_max - SC_Real_min)) + SC_norm_min)

        #print self.SC_Pure
        #print self.SC_norm
        #quit()
        self.perf_Pure = Splitted[4]
        self.perf = int(self.perf_Pure); self.reward = self.perf; self.R = 0; self.done = False;

        #self.SC_temp, self.SC_norm, self.SC_feed = calc_energy_prod_consu(self.time_temp, self.Init_SC_Volt, self.Light)


        # Normalize all parameters from 0 to 1 before feeding the RL
        #self.Light_feed = (self.Light - Light_min)/float((Light_max - Light_min))

        stuff = []
        for i in range(len(diction_feat)):
            tocheck = diction_feat[i]
            feature = checker(tocheck, self.SC_Pure, self.SC_norm, self.Light, self.curr_time_h, self.curr_time_m, self.week)
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

        return s, s_, old, self.perf, self.reward

    def Envi(self, action, tot_action, diction_feat, granul, s_, old, Input_Data, Sleep):
        # Reward Based on Action and Environment
        #print(Input_Data)

        '''
        with open(Input_Data) as f:
            self.content = f.readlines()
        self.content = [x.strip() for x in self.content]
        '''

        with FileReadBackwards(Input_Data, encoding="utf-8") as frb:
            # getting lines by lines starting from the last line up
            for new in frb:
                #print(old)
                #Splitted = old.strip().split("|")
                #if len(Splitted) > 7 and int(Splitted[5]) != 0 and Splitted[5].isdigit():
                #    break

        #for i in range(1,len(self.content)):
            #new = self.content[-i]
                Splitted = new.split("|")
                #print(new)
                #print(Splitted)
                #print(Splitted[5])
                if old == new and self.Node_Death == False: # The Node is not death and probably it did not read a new data yet. Hence we don't have to learn here
                    Skip = True
                    print("There aren't new data available. Retry...")
                    return self.reward, self.done, s_, Skip, old, self.Node_Death, int(self.perf_Pure)

                elif old == new and self.Node_Death == True:  # Node is Death, so I will fake future time so it will keep learning while the node is Death
                    #print self.curr_time_next
                    self.curr_time_next = self.curr_time_next + datetime.timedelta(0, Sleep)
                    #print self.curr_time_next
                    self.curr_time_m_next = min(self.T_m_List, key=lambda x:abs(x-self.curr_time_m_next))
                    self.curr_time_next = datetime.datetime(self.curr_time_next.year, self.curr_time_next.month, self.curr_time_next.day, self.curr_time_next.hour, self.curr_time_next.minute)

                    self.reward, self.perf_next, self.Node_Death = simple_barath_sending_and_dying_rew(action, tot_action, self.SC_norm_next, self.perf, SC_norm_min, granul)
                    Skip = False
                    return self.reward, self.done, s_, Skip, old, self.Node_Death, int(self.perf_Pure)

                elif len(Splitted) > 7 and Splitted[5].isdigit() and int(Splitted[5]) != 0:
                    break

        #print "Envi: " + self.content[-1]
        #Date = Splitted[0].split(" ")
        #Split_Date = Date[0].split("/")
        #self.Year_next = int(Split_Date[2])
        #self.Day_next = int(Split_Date[1])
        #self.Month_next = int(Split_Date[0])
        #Time = Date[1].split(":")
        #self.curr_time_h_next = int(Time[0])
        #self.curr_time_m_next = int(Time[1])
        time = datetime.datetime.strptime(Splitted[0], '%m/%d/%y %H:%M:%S')
        self.Year_next = time.year
        self.Day_next = time.day
        self.Month_next = time.month
        self.curr_time_h_next = time.hour
        self.curr_time_m_next = time.minute

        self.curr_time_m_next = min(self.T_m_List, key=lambda x:abs(x-self.curr_time_m_next))
        self.curr_time_next = datetime.datetime(self.Year_next, self.Month_next, self.Day_next, self.curr_time_h_next, self.curr_time_m_next)
        week_day = datetime.datetime.strptime(Splitted[0], '%m/%d/%y %H:%M:%S').strftime('%a')
        if week_day == "Sat" or week_day == "Sun":
            self.week = 0
        else:
            self.week = 1
        #self.curr_time_h_feed = (self.curr_time_h - self.Time_h_min)/float((self.Time_h_max - self.Time_h_min))
        #self.curr_time_m_feed = (self.curr_time_m - 0)/float((self.Time_m_max - 0))

        Light_Pure = int(Splitted[8])
        if Light_Pure > Light_Real_max:
            Light_Pure = Light_Real_max

        # Normalize Light from 0 % 4000 to 0 % 10 with NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        self.Light_Pure = min(self.Light_List, key=lambda x:abs(x-Light_Pure))
        self.Light_next = (((self.Light_Pure - Light_Real_min) * (Light_max - Light_min)) / (Light_Real_max - Light_Real_min)) + Light_min

        # Normalize SC_Volt from 100 % 0 to 0 % 10
        self.SC_Pure_next = int(Splitted[5])

        self.SC_Pure_float_next = (self.SC_Pure_next/100.0)*5.4

        if self.SC_Pure_float_next > SC_Real_max:
            self.SC_Pure_float_next = SC_Real_max

        self.SC_norm_next = round((((self.SC_Pure_float_next - SC_Real_min) * (SC_norm_max - SC_norm_min)) / (SC_Real_max - SC_Real_min)) + SC_norm_min)

        self.perf_Pure = Splitted[4]
        self.perf = int(self.perf_Pure);

        self.reward, self.perf_next, self.Node_Death = simple_barath_sending_and_dying_rew(action, tot_action, self.SC_norm_next, self.perf, SC_norm_min, granul)
        #reward, perf_next = rp.simple_light_rew(action, Light, perf)

        self.perf_Pure = int(Splitted[4])

        # Adjust Performance and Time
        self.perf_next = adjust_perf(self.perf_next, granul)  #time_temp = 600

        self.R += self.reward

        if self.curr_time >= self.end_time:
            self.done = True

        for i in range(len(diction_feat)):
            tocheck = diction_feat[i]
            feature = checker(tocheck, self.SC_Pure_next, self.SC_norm_next, self.Light_next, self.curr_time_h_next, self.curr_time_m_next, self.week)
            s_[i] = feature

        Skip = False
        #self.done = True
        return self.reward, self.done, s_, Skip, new, self.Node_Death, int(self.perf_Pure)

    def Update_s(self, action, diction_feat, s, granul):
        # Append Data

        #print self.reward/100
        self.SC_Pure_float = (self.SC_Pure/100.0)*5.4
        #print self.SC_Pure_float
        self.Light_hist.append(self.Light); self.Action_hist.append(action); self.reward_hist.append(self.reward); self.Time_hist.append(self.curr_time); self.perf_hist.append(self.perf); self.SC_Pure_hist.append(self.SC_Pure_float); self.SC_norm_hist.append(self.SC_norm);

        # swap observation
        for i in range(len(diction_feat)):
            tocheck = diction_feat[i]
            feature = checker(tocheck, self.SC_Pure_next, self.SC_norm_next, self.Light_next, self.curr_time_h_next, self.curr_time_m_next, self.week)
            s[i] = feature
        #s = s_;
        self.perf = self.perf_next;
        self.Light = self.Light_next;
        self.curr_time = self.curr_time_next; self.curr_time_h = self.curr_time_h_next; self.curr_time_m = self.curr_time_m_next;
        self.SC_norm = self.SC_norm_next; self.SC_Pure = self.SC_Pure_next;

        return s

    def Saving(self, Text, episode, tot_episodes):

        self.Light_Best = self.Light_hist; self.Action_Best = self.Action_hist; self.reward_Best = self.reward_hist; self.best_reward = self.R; self.Time_Best = self.Time_hist; self.perf_Best = self.perf_hist; self.SC_Pure_Best = self.SC_Pure_hist
        self.SC_Best_norm_hist = self.SC_norm_hist;

        plot_legend_text(self.Time_Best, self.Light_Best, self.Action_Best, self.reward_Best, self.perf_Best, self.SC_Pure_Best, self.SC_Best_norm_hist, Text, self.best_reward, episode)
        #plot_reward_text(self.Tot_Episodes, self.Tot_Reward, Text, self.best_reward, episode)
        with open('Saved_Data/Graph_hist_' + Text + '.pkl', 'wb') as f:  # Python 3: open(..., 'wb')
            pickle.dump([self.Light_Best, self.Action_Best, self.reward_Best, self.best_reward, self.Time_Best, self.perf_Best, self.SC_Pure_Best, self.SC_Best_norm_hist, self.Tot_Episodes, self.Tot_Reward, Text, episode], f, protocol=2)


def simple_barath_sending_and_dying_rew(action, tot_action, SC_norm, perf, SC_norm_min, granul): # not finished yet
    '''
    if tot_action == 3:
        if action == 2:
            perf += 1;
        if action == 1:
            perf += 0
        if action == 0:
            perf -= 1
    else:
        print("Error")
        exit()
    '''
    #f = open("action.txt","w+")
    #f.write(str(action))
    #f.close()
    #print "Action Writed: " + str(action)

    #print "here hrehrehrehrehr"
    perf = action

    if perf > len(granul)-1:
    	perf = len(granul)-1
    if perf < 0:
    	perf = 0

    # every time you send a data in 15mins you get 1000 points
    if perf == 3:
        #reward = 4000
        reward = 3
    elif perf == 2:
        #reward = 3000
        reward = 2
    elif perf == 1:
        #reward = 2000
        reward = 1
    elif perf == 0:
        #reward = 1000
        reward = 0

    #print SC_norm

    if SC_norm <= SC_norm_min_die:
        reward = - 300
        Node_Death = True
        print("Node_Death: Adding Time Automatically")
    else:
        Node_Death = False

    if perf == 0 and SC_norm <= SC_norm_min_die:
        reward = - 100

    return reward, perf, Node_Death

def adjust_perf(perf, granul):

    if perf > len(granul) - 1:
    	perf = len(granul) - 1
    if perf < 0:
    	perf = 0

    return perf

def plot_reward_text(Tot_Episodes, Tot_Reward, Text, best_reward, tot_episodes):
    #Start Plotting
    fig, ax = plt.subplots(1)
    #fig.autofmt_xdate()
    plt.plot(Tot_Episodes, Tot_Reward, 'r', label = 'Total Reward')
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
    fig.savefig('Images-Auto/Reward_' + Text + '.png', bbox_inches='tight')
    #plt.show()
    plt.close(fig)

def plot_legend_text(Time_Best, Light_Best, Action_Best, reward_Best, perf_Best, SC_Pure_Best, SC_Best_norm_hist, Text, best_reward, tot_episodes):
    #Start Plotting
    try:
        fig, ax = plt.subplots(1)
        fig.autofmt_xdate()
        plt.plot(Time_Best, Light_Best, 'b', label = 'Light')
        plt.plot(Time_Best, Action_Best, 'y*', label = 'Action',  markersize = 15)
        plt.plot(Time_Best, reward_Best, 'k+', label = 'Reward')
        plt.plot(Time_Best, perf_Best, 'g', label = 'Performance')
        plt.plot(Time_Best, SC_Pure_Best, 'r+', label = 'SC_Voltage')
        plt.plot(Time_Best, SC_Best_norm_hist, 'm^-', label = 'SC_Voltage_Normalized')
        #plt.plot(Time_Best, SC_Best_norm_hist, 'm')
        plt.title(Text + ', Best_R: ' + str(best_reward) + ', Epis: ' + str(tot_episodes), fontsize=15)
        plt.ylabel('Super Capacitor Voltage[V]', fontsize=15)

        xfmt = mdates.DateFormatter('%m-%d-%y %H:%M:%S')
        ax.xaxis.set_major_formatter(xfmt)
        ax.tick_params(axis='both', which='major', labelsize=10)

        legend = ax.legend(loc='center right', shadow=True)
        plt.legend(loc=9, prop={'size': 10})
        plt.xlabel('Time[h]', fontsize=20)
        ax.grid(True)
        fig.savefig('Saved_Data/Graph_' + Text + '.png', bbox_inches='tight')
        #plt.show()
        plt.close(fig)
    except:
        print(Time_Best, Light_Best, Action_Best, reward_Best, perf_Best, SC_Pure_Best, SC_Best_norm_hist, Text, best_reward, tot_episodes)
        print("There was a problem while saving data. Check and Fix")
        quit()

def checker(tc, SC_real, SC_norm, Light, curr_time_h, curr_time_m, week):
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
