"""
Reinforcement learning for ACES by Francesco Fraternali.
The RL is in RL_brain.py.
"""

from RL_brain import QLearningTable
import numpy as np
from Reward_Policies_Func_Sim import Env_Rew_Pol_Sim
import time
import datetime
from subprocess import PIPE, Popen, call
import os
import string
import shutil
import smtplib

with open("ID_RL.txt", 'r') as f:
    content = f.read()
content_split = content.strip().split(',')
ID = content_split[0]
features = content_split[1]
feat = features.split('|')
Device = content_split[2]

dirpath = os.getcwd()
ID = os.path.basename(dirpath)

Epsilon_max = 1
Epsilon_min = 0.1
tot_action = 4
steps = 1
epsi_steps = 0.004
tot_episodes = int((Epsilon_max - Epsilon_min)/epsi_steps)
diction = {'SC_norm':'SC_n', 'Light': 'Light', 'week': 'wk'}

Text_list = [ID, '_' , Device, '_']

def update(start_day, end_day):
    if learn_single_day:
        print("\nStarting Testing ...")
    else:
        print("\nStarting Training ...")

    Environ = Env_Rew_Pol_Sim(start_day, end_day)
    for episode in range(0, tot_episodes):

        s, s_ = Environ.Init(feat, episode)
        while True: # this loop lasts one day
            # RL choose action based on observation
            action = RL.choose_action(str(s), Text)

            reward, done, s_ = Environ.Envi(action, feat, s_)

            # RL learn from this transition
            epsilon = RL.learn(str(s), action, reward, str(s_), Text, episode, epsi_steps)

            s = Environ.Update_s(action, feat, s, episode)

            # break while loop when end of this episode
            if done:
                break

        if (episode % 50 == 0 and learn_single_day == False):
            Environ.printing(Text, episode, tot_episodes, epsilon, 0)

        if learn_single_day:
            if done:
                Environ.printing(Text, episode, tot_episodes, epsilon, 1)
                break
    RL.save(episode, Text)
    print('Game Over and Save Data')

def find_Q_Table(day):
    proc = Popen("ls Q_Tables", stdout=PIPE, shell=True)
    (out, err) = proc.communicate()
    out = out.decode()
    spl = out.strip().split('\n')
    #print(spl)
    Q_found = "Q_Table_10"

    try:
        for file in spl:
            spli = file.split('.')
            lis = spli[0].split('_')
            for i in range(1, len(lis)):
                if lis[-i].isdigit():
                    if int(lis[-i]) > day:
                        print("Found QTable: " + str(file))
                        Q_found = file
                        day = int(lis[-i])
                else:
                    break
    except:
        print("No valid Q_Tables found...")

    return Q_found, day

if __name__ == "__main__":

    print("Starting ACES Simulator...")
    print("Checking Older Version of Q-Tables...")
    check_start_day = 10
    Text = ''.join(str(elem) for elem in Text_list)

    day = 10

    Q_found, day = find_Q_Table(day)
    spl = Q_found.split('_')
    spl.remove('Q')
    spl.remove('Table')
    spl[-1] = day

    Text_Table = "_".join(str(elem) for elem in spl)

    print("Epsilon Steps (Delta): " + str(epsi_steps))
    time.sleep(1)

    very_start_day = 0  # day 1 is 0
    very_end_day = 900 # 40 means 4th day
    num_days = (very_end_day - very_start_day)/10
    day = 10
    Text_list.append(str(day))
    Text = ''.join(str(elem) for elem in Text_list)

    for i in range(0, int(num_days)*10):
        if i == 0:
            use_new_table = True
        else:
            use_new_table = False
        Text_Table = Text

        if day % 10 == 0:
            learn_single_day = False
            epsilon = 0.1
            start_day = very_start_day
            end_day = day
        else:
            learn_single_day = True
            epsilon = 1
            start_day = day - 5
            end_day = start_day + 10
        Text = ''.join(str(elem) for elem in Text_list)
        print("Day: ", str(day/10), ", Exp name: ", Text, ", Use new Table: ", use_new_table, ", epsilon: ", epsilon, ", Train(False)/Test(true): ", learn_single_day)
        time.sleep(5)
        RL = QLearningTable(actions=list(range(tot_action)), Text=Text, Text_Table=Text_Table, use_new_table=use_new_table,epsilon=epsilon)
        update(start_day, end_day)
        day += 5
        Text_list[-1] = day
