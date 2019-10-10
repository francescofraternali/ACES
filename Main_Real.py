"""
Reinforcement learning.
The RL is in RL_brain.py.

One cool thing to do: put a pattern of the presence of people and check if it can predict that
"""

from RL_brain_General import QLearningTable
import numpy as np
from Reward_Policies_Func_Sim import Env_Rew_Pol_Sim
from Reward_Policies_Func_Real import Env_Rew_Pol_Real
import time
import datetime
from subprocess import PIPE, Popen, call
import threading
import os
import string
import shutil
import smtplib

SaveDataFold = "Saved_Data/"
#ID_BLE_path = ""

with open("ID_RL.txt", 'r') as f:
    content = f.read()

content_split = content.strip().split(',')
#Text = content_split[0]
BS_ID = content_split[0]
features = content_split[1]
feat = features.split('|')
Device = content_split[2]

dirpath = os.getcwd()
BS_ID = os.path.basename(dirpath)
#print(BS_ID)

with open("ID_BLE.txt", 'r') as f:
    for line in f:
        splt = line.strip().split(',')
        if splt[0] == Device:
            File_name = splt[1]


with open('info_BS.txt') as f:
    for line in f:
        line = line.strip().split('=')
        if line[0] == "pwd":
            pwd = line[1]
        elif line[0] == "bs_name":
            bs_name = line[1]


granularity = "15min" # see option above
granul = [900, 900, 900, 900] # as Reality

Epsilon_max = 1
Epsilon_min = 0.35
tot_episodes = 20000; tot_action = 4
steps = (tot_episodes)/10
steps = 1
epsi_steps = (Epsilon_max - Epsilon_min)/7
epsi_steps = 0.0007 #0.00007
save_rate = 5000
#epsi_steps = 0.0004
diction = {'SC_norm':'SC_n', 'Light': 'Light', 'week': 'wk'}

Text_list = [BS_ID, '_' ,Device,"_PIR_"]
check_max = 5

# My stuff over

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.stdout = None
        self.stderr = None

    def run(self, timeout):
        def target():
            #print('Thread started')
            self.process = Popen(self.cmd,  stdout=PIPE, stderr=PIPE, shell=True)
            self.stdout, self.stderr = self.process.communicate()
            #print('Thread finished')

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        try:
            if thread.is_alive():
                #print('Terminating process')
                self.process.terminate()
                thread.join()
        except:
            print("something wrong in the process. Maybe it was already terminated?")

        return self.stdout, self.stderr, self.process.returncode



def update_Simula(Light_Input):
    print("Starting Simula...")
    Environ = Env_Rew_Pol_Sim(granul, Light_Input)
    for episode in range(0,tot_episodes):
        #past = 0
        #count = 0
        #action_dc = - 1
        #s_ = s
        s, s_ = Environ.Init(feat, granul, granularity, episode)
        while True: # this loop lasts one day

            # RL choose action based on observation
            action = RL.choose_action(str(s), Text)

            #if past == 0:
            #    action = 1
            #else:
            #    action = 1

            #if count % 1 == 0:
            #    action_dc = 3
            #else:
            #    action_dc = 1

            action_dc = 0

            reward, done, s_ = Environ.Envi(action, tot_action, feat, granul, s_, granularity, action_dc)


            #print("before", s, action, reward, s_)
            #time.sleep(1)
            # RL learn from this transition
            epsilon, Converge = RL.learn(str(s), action, reward, str(s_), Text, tot_action, granul, episode, steps, epsi_steps, Simula)

            #print(s, action, reward, s_)


            s = Environ.Update_s(action, feat, s, granul, episode, save_rate, action_dc)

            #past += 1
            #count += 1
            # break while loop when end of this episode

            if done:
                #print("count: " + str(count))
                break


        if Converge:
            break
        if (episode % 100 == 0):
            Environ.printing(Text, episode, tot_episodes, epsilon, 0)
        if episode % save_rate == 0:
            Environ.saving(Text, episode, tot_episodes, epsilon, 1)
        #if (episode % 1000 == 0):
        #    RL.save(episode, Text)

        # end of game
    Environ.saving(Text, episode, tot_episodes, epsilon, 1)
    RL.save(episode, Text)
    print('Simulation Over and Data Saved')


def update_Real():
    print("Initializing Real...")
    Environ = Env_Rew_Pol_Real()
    print("Synching ID_File")
    sync_ID_file()
    for episode in range(0,1): #24*4 so it will last one day

        Skip = False
        skip_true = 0
        skip_dead = 10
        Node_Death = False
        Sleep = granul[0]
        
        #sync_input_data()
        #sync_ID_file()

        s, s_, old, perf, reward = Environ.Init(feat, granul, File_name)
        while True: # this loop lasts one day

            # RL choose action based on observation
            if Skip == False:
                action = RL.choose_action(str(s), Text)
                sync_action(action)

            Splitted = old.split('|')
            toPrint = Splitted[0] + "|" + Splitted[1] + "|" + Splitted[4] + "|" + Splitted[5] + "|" + Splitted[6] + "|" + Splitted[7] + "|" + Splitted[8]

            if action == 0 and int(Splitted[5]) < 56:
                print("Block True, Node Dying but at least he knows what he is doing")
            elif int(Splitted[5]) < 56:
                sync_action('0')
                print("Block True, Node Dying, Action Imposed to 0")

            #if action == 3 and int(Splitted[5]) >= 92:
            #    print("Node full of energy but at least he knows what he is doing (Action = 3)")
            #elif int(Splitted[5]) >= 97:
            #    sync_action('3')
            #    print("Wake up, Node Full of Energy, Action Imposed to 3")
            #print("ID: " +str(BS_ID) + "_" +str(Device) + ", Last_Data: " + str(toPrint) + ", Skip: " + str(Skip) + ", Next_Act: " + str(action) + ", Wait[s]: " + str(Sleep))
            print("ID: {0}_{1}, Last_Data: {2}, Skip: {3}, Next_Act: {4}, Wait[s]: {5}".format(str(BS_ID), str(Device), str(toPrint), str(Skip), str(action), str(Sleep)))
            time.sleep(900) # sleep while waiting for next data
            #sync_input_data()

            reward, done, s_, Skip, new, Node_Death, perf = Environ.Envi(action, tot_action, feat, granul, s, old, File_name, Sleep)

            #RL learn from this transition
            if Skip == False or Node_Death == True:
                #print("Learn this on " + str(BS_ID) + ': ' + str(s)+ ', ' + str(action) + ', ' + str(reward) + ', ' + str(s_))
                RL.learn(str(s), action, reward, str(s_), Text, tot_action, granul, episode, steps, epsi_steps, Simula)
                s = Environ.Update_s(action, feat, s, granul)
                Environ.Saving(Text, episode, tot_episodes)
                RL.save(episode, Text)

            old = new

            if Skip == True:
                skip_true += 1
                if skip_true > 2 and int(Splitted[5]) >= 56 and Node_Death == False:
                    message = "Too many skip_true. Somethign wrong, please check. Resetting Base Station."
                    send_email(message)
                    time.sleep(1)
                    print(message)
                    call("sshpass -p " + pwd +" ssh "+bs_name+" sudo reboot", shell=True)
                    time.sleep(120)
                    skip_true = 0
                elif skip_true > skip_dead and int(Splitted[5]) < 56:
                    message = "Node is dead, reducing number of messages sent"
                    send_email(message)
                    #time.sleep(1)
                    #subprocess.call("sshpass -p " + pwd +" ssh "+bs_name+" sudo reboot", shell=True)
                    skip_true = 0
                    skip_dead += 96 # After it tells that the node is death it keeps telling me every more days
            else:
                skip_true = 0
                skip_dead = 10

            #done = True
            # break while loop when end of this episode
            if done:
                break

        #if learn_single_day:
        #    if done:
        #        break
        # end of game
    RL.save(episode, Text)
    print('Real Over and Save Data')
    time.sleep(5)

def send_email(message):
    for i in range(10):
        try:
            msg="""\
            Subject: Hi there unfortunantely

            Problem on {BS_ID} for device {Device}. Message: {message}"""

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login("name.uniquesurname@gmail.com", "Wlastik7")
            server.sendmail(
              "name.uniquesurname@gmail.com",
              "name.uniquesurname@gmail.com",
              msg.format(BS_ID=BS_ID, Device=Device, message=message))
            server.quit()
            time.sleep(2)
            break
        except:
            print("Could not send email. Something wrong Check code with message: {0}".format(message))
            time.sleep(60)

def checker(message, timeout):
    global check_max
    command = Command(message)
    for i in range(0, check_max):
        #try:
        (out, err, check) = command.run(timeout=60)

        if check == -15:
            print("Base Station not answering. Trial num: " + str(i))
            time.sleep(900)
        else:
            break

    if check == -15:
        check_max += 10
        message = "Base station not aswering, something wrong, resetting base station..."
        for i in range(10):
            try:
                send_email(message)
                time.sleep(2)
                break
            except:
                print("Could not send Email. Something wrong. Check on -sync_input_data- funtion. Trial num: " + str(i))
                time.sleep(60)

        print(message)
        call("sshpass -p " + pwd +" ssh "+bs_name+" sudo reboot", shell=True)
        time.sleep(120)
    else:
        check_max = 5

    return out, check

def sync_input_data():

    #proc = subprocess.Popen("sshpass -p " + pwd +" scp -r -o StrictHostKeyChecking=no "+bs_name+":/home/pi/BLE_GIT/Data/"+File_name+" .", stdout=subprocess.PIPE, shell=True)
    #command = "sshpass -p " + pwd +" scp -r -o StrictHostKeyChecking=no "+bs_name+":/home/pi/BLE_GIT/Data/" + File_name + " Temp_"+ File_name
    command = "sshpass -p {0} scp -r -o StrictHostKeyChecking=no {1}:/home/pi/BLE_GIT/Data/{2} " + SaveDataFold + "Temp_{2}".format(pwd, bs_name, File_name)
    #command = "sshpass -p " + val + " scp -r -o StrictHostKeyChecking=no " + key +":/home/pi/BLE_GIT/Data/"+ file + " Files/Temp_" + file
    out, check = checker(command, 60)

    if check == 0: #Everything went right
        with open(File_name, 'ab') as outfile:
            with open(SaveDataFold + "Temp_" + File_name, 'rb') as infile:
                outfile.write(infile.read())

        #print("Removing file ...")
        time.sleep(1)
        #command ="sshpass -p " + val + " ssh " + key +" rm /home/pi/BLE_GIT/Data/"+ file
        #command = "sshpass -p " + pwd +" ssh " + bs_name + " rm /home/pi/BLE_GIT/Data/" + File_name
        command = "sshpass -p {0} ssh {1} rm /home/pi/BLE_GIT/Data/{2}".format(pwd, bs_name, File_name)
        out, check = checker(command, 60)
        #command = "rm Temp_" + File_name
        command = "rm "+ SaveDataFold + "Temp_{0}".format(File_name)
        out, check = checker(command, 60)
        #print(check)
    elif check == 1:
        print("No new file to merge")


def sync_ID_file():

    call("sshpass -p " + pwd +" scp -r -o StrictHostKeyChecking=no ID_BLE.txt "+bs_name+":/home/pi/BLE_GIT/ID/ID.txt", shell=True)

def sync_action(action):
    run = 0
    for num_attemps in range(3):
        try:
            # Now Let's update the action
            with open("ID_BLE.txt", 'r') as f:
                lines = f.read().splitlines()
                count = 0
                for line in lines:
                    elements = line.strip().split(',')
                    #print(elements)
                    if elements[0] == Device:
                        new = []
                        for i in range(len(elements)):
                            if i == 1:
                                new.append(str(File_name))
                            elif i == 2:
                                new.append(str(action))
                            else:
                                new.append(elements[i])
                        new_line = ','.join(new)
                        #print(new_line)
                        lines[count] = new_line
                    count += 1

            with open('output_file.txt','w') as g:
                g.write('\n'.join(lines))


            os.remove('ID_BLE.txt')
            #sleep(0.5)
            #shutil.move('output_file.txt','../BLE/')
            time.sleep(0.5)
            os.rename('output_file.txt','ID_BLE.txt')

            run = 1
        except:
            print("Something wrong while updating actions.")

        if run == 1:
            break

    if run == 0:
        send_email("Something wrong while synching actions. Check!")

    #print("sshpass -p "+pwd+" scp -r -o StrictHostKeyChecking=no ../BLE/ID.txt "+bs_name+":/home/pi/BLE_GIT/BaseStation")
    call("sshpass -p "+pwd+" scp -r -o StrictHostKeyChecking=no ID_BLE.txt "+bs_name+":/home/pi/BLE_GIT/ID/ID.txt", shell=True)

def find_Q_Table(day):
    proc = Popen("ls Q_Tables", stdout=PIPE, shell=True)
    (out, err) = proc.communicate()
    out = out.decode()
    spl = out.strip().split('\n')
    print(spl)
    #if spl[0]== "":
        #print("No Q tables found")
    Q_found = "Q_Table_10"
    
    try:
        for file in spl:
            #print("here")
            spli = file.split('.')
            lis = spli[0].split('_')
            #print(lis)
            for i in range(1, len(lis)):
                #print(lis[-i])
                if lis[-i].isdigit():
                    if int(lis[-i]) > day:
                        print("Found QTable: " + str(file))
                        Q_found = file
                        day = int(lis[-i])
                else:
                    #print("break")
                    break
    except:
        print("No valid Q_Tables found...")

    return Q_found, day


if __name__ == "__main__":

    print("Starting ACES_GIT...")
    print("Checking Older Version of Q-Tables...")
    check_start_day = 10
    Text = ''.join(str(elem) for elem in Text_list)

    day = 10
    #print(spl,len(spl))

    Q_found, day = find_Q_Table(day)
    spl = Q_found.split('_')
    spl.remove('Q')
    spl.remove('Table')
    spl[-1] = day

    Text_Table = "_".join(str(elem) for elem in spl)

    time.sleep(1)

    #print("Synching Data...")
    #sync_ID_file()
    #sync_input_data()

    #print("Testing Email...")
    #message = "Email Test"
    #send_email(message)


    time.sleep(0.5)
    Start_Real_Time = datetime.datetime.now()
    File_Begin_Time = datetime.datetime.now() - datetime.timedelta(0, ((day/10)*24*60*60))
    #File_Begin_Time = datetime.datetime.strptime(Start_Real_Time, '%m/%d/%y %H:%M:%S')
    #File_Begin_Time = Start_Real_Time.strftime('%m/%d/%y %H:%M:%S')
    print("Beginning Experiment is: " + str(File_Begin_Time))
    time.sleep(0.5)
    print("Steps and Epsilon Steps: " + str(steps) + ", " + str(epsi_steps))
    time.sleep(0.5)
    very_start_day = 0  # day 1 is 0
    #num_days = (very_end_day - very_start_day)/10
    Text_list.append(str(day))
    Text = ''.join(str(elem) for elem in Text_list)
    #Text_Table = Text


    while True:
        if day == 10:
            use_new_table = True
            #day = 10
            #Text_list[-1] = day
            #Text = ''.join(str(elem) for elem in Text_list)
        else:
            use_new_table = False


        if day % 10 == 0: # Run or Re-Run Simulation in case it was not completed
            #learn_single_day = False
            epsilon = Epsilon_min
            Simula = True
            start_day = very_start_day
            end_day = day

        else: # Learn from Real-World
            #learn_single_day = True
            epsilon = Epsilon_max
            Simula = False
            start_day = day - 5
            end_day = start_day + 10

        print("What: " + Text + ", Use New Table: " + str(use_new_table) + ", Epsilon: " + str(epsilon) +  ", Simula: " + str(Simula))
        time.sleep(2)

        RL = QLearningTable(actions=list(range(tot_action)), Text=Text, Text_Table=Text_Table, use_new_table=use_new_table, epsilon=epsilon)
        if Simula == 1:
            end_sim_dt = datetime.datetime.now()
            end_sim = end_sim_dt.strftime('%m/%d/%y %H:%M:%S')

            #start_sim_dt = end_sim_dt - datetime.timedelta(0, ((end_day/10)*24*60*60))
            if end_day >= 150:
                end_day = 150
            start_sim_dt = end_sim_dt - datetime.timedelta(0, ((end_day/10)*24*60*60)) # So I only use the last 15 days for learning
            start_sim = start_sim_dt.strftime('%m/%d/%y %H:%M:%S')
            #start_sim = File_Begin_Time.strftime('%m/%d/%y %H:%M:%S')
            #end_sim = File_Begin_Time + datetime.timedelta(0, ((end_day/10)*24*60*60)) # I am not using this
            print("Generating Light Data from " + str(start_sim) + " to " + str(end_sim))
            os.system('python3 Generate_Light.py ' + str(start_sim) + ' ' + str(end_sim) + ' ' + str(Text) + ' ' + str(File_name))
            Light_Input = Text + "_Adapted.txt"
            update_Simula(Light_Input)
        else:
            update_Real()

        Text_Table = Text
        day += 5
        Text_list[-1] = day
        Text = ''.join(str(elem) for elem in Text_list)
    #env.after(100, update)
    #env.mainloop()
