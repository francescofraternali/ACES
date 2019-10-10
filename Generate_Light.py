"""
Generating Light
"""

import os
import numpy as np
import datetime
import time
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import sys

print("Starting Adapting Light...")
start_sim_1 = sys.argv[1]
start_sim_2 = sys.argv[2]
end_sim_1 = sys.argv[3]
end_sim_2 = sys.argv[4]
Text = sys.argv[5]
Input_Data = sys.argv[6]
granularity = int(sys.argv[7])

start_sim = str(start_sim_1) + ' ' +str(start_sim_2)
end_sim = str(end_sim_1) + ' ' + str(end_sim_2)
#print start_sim
#print end_sim
#print Text
print(Input_Data)
#time.sleep(2)

Light_Real_min = 0; Light_Real_max= 2000; Light_max = 10; Light_min = 0

T_m_List = []
steps = granularity/60
for i in range(0, 60, 15):
    T_m_List.append(i)

#Text = "Stairs_RL_Pible"

try:
    os.remove(Text + "_Adapted.txt")
except:
    a = 0
#time.sleep(2)

with open(Input_Data) as f:
    content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content]

Light_hist = []; Perf_hist = []; Time_hist = []; SC_norm_hist = []; SC_Pure_hist = []; SC_temp_hist =[]
Light_Adapt_hist = []; Time_Adapt_hist = [];

#Splitted = content[0].split("|")
#Date = Splitted[0].split(" ")
#Split_Date = Date[0].split("/")
#Year = int(Split_Date[2])
#Day = int(Split_Date[1])
#Month = int(Split_Date[0])
#Time = Date[1].split(":")
#curr_time_h = int(Time[0])
#curr_time_m = int(Time[1])

#Start_Real_Time = datetime.datetime.now()
#Starting_time = datetime.datetime(18,Month,Day,curr_time_h,curr_time_m,05)
Starting_time = datetime.datetime.strptime(start_sim, '%m/%d/%y %H:%M:%S')
Ending_time = datetime.datetime.strptime(end_sim, '%m/%d/%y %H:%M:%S')
Starting_next = Starting_time + datetime.timedelta(0, granularity)
Starting_next = Starting_time
Light_sum = []
#print Starting_time
#print Starting_next

for i in range(0,len(content)):
    Splitted = content[i].split("|")
    #print Splitted
    try:
        if len(Splitted) > 7:
            Date = Splitted[0].split(" ")
            Split_Date = Date[0].split("/")
            Year = int(Split_Date[2])
            Day = int(Split_Date[1])
            Month = int(Split_Date[0])
            Time = Date[1].split(":")
            curr_time_h = int(Time[0])
            curr_time_m = int(Time[1])


            curr_time_m = min(T_m_List, key=lambda x:abs(x-curr_time_m))
            #curr_time_m = min(T_m_List, key=lambda x:abs(x-self.curr_time_m))
            #curr_time = datetime.datetime(Year,Month,Day,curr_time_h,curr_time_m)
            curr_time = datetime.datetime.strptime(Splitted[0], '%m/%d/%y %H:%M:%S')
            #end_time = datetime.datetime(2018,2,2,curr_time_h,curr_time_m)

            node = Splitted[1]
            perf = Splitted[4]
            Batt = Splitted[5]
            PIR = Splitted[6]
            Reed = Splitted[7]

            Light_Pure = int(Splitted[8])


            if Light_Pure > Light_Real_max:
                Light_Pure = Light_Real_max

            #Light_Pure = Light_used * 200
            Light = (((Light_Pure - Light_Real_min) * (Light_max - Light_min)) / (Light_Real_max - Light_Real_min)) + Light_min


            # Calculate Light for Simulation
            if curr_time <= Starting_next:
                #print "Load", Splitted[0]
                Light_sum.append(Light_Pure)
                #print Splitted[0], Light_Pure
            elif curr_time > Starting_next:
                while True:
                    if len(Light_sum) is not 0:
                        #print "Lenght", len(Light_sum)
                        with open(Text + '_Adapted.txt', "a") as myfile:
                            final_time = Starting_next.strftime('%m/%d/%y %H:%M:%S')
                            Append = final_time + '|' + node + "|||" + perf + '|' + Batt + '|' + PIR + '|' + Reed + '|' + str(int(np.mean(Light_sum))) + "\n"
                            #print "Write: " + final_time + '|' + node + "|||" + perf + '|' + Batt + "|0|0|" + str(int(np.mean(Light_sum)))
                            myfile.write(Append)
                            Light_Adapt_hist.append(int(np.mean(Light_sum)))
                            Time_Adapt_hist.append(Starting_next)
                            #time.sleep(1)
                            Light_old = int(np.mean(Light_sum))
                            Light_sum = []
                            block = 0
                    #print curr_time
                    if block == 0:
                        Starting_next = Starting_next + datetime.timedelta(0, granularity)
                    #print "Next Starting", Starting_next
                    if curr_time <= Starting_next:
                        Light_sum = []
                        Light_sum.append(Light_Pure)
                        #print "c'e' roba"
                        break
                    else:
                        with open(Text + '_Adapted.txt', "a") as myfile:
                            final_time = Starting_next.strftime('%m/%d/%y %H:%M:%S')
                            Append = final_time + '|' +'|' + '|' + '|' + '|' + "|0|0|" + str(int((Light_old + Light_Pure)/2)) + "\n"
                            #print "Write Empty: " + final_time + '|' + node + "|||" + perf + '|' + Batt + "|0|0|" + str(int((Light_old + Light_Pure)/2))
                            myfile.write(Append)
                            Light_Adapt_hist.append(Light_old)
                            Time_Adapt_hist.append(Starting_next)
                            Light_old = int((Light_old+Light_Pure)/2)
                            Starting_next = Starting_next + datetime.timedelta(0, granularity)
                            #print "Next Starting Empty", Starting_next
                            block = 1


            Light_hist.append(Light_Pure); Time_hist.append(curr_time);
    except:
        continue

#print(Starting_next)
#print(Ending_time)
while Starting_next < Ending_time :
    Light_old = 0
    with open(Text + '_Adapted.txt', "a") as myfile:
        final_time = Starting_next.strftime('%m/%d/%y %H:%M:%S')
        Append = final_time + '|' +'|' + '|' + '|' + '|' + "|0|0|" + str(int(Light_old)) + "\n"
        #print "Write Empty: " + final_time + '|' + node + "|||" + perf + '|' + Batt + "|0|0|" + str(int((Light_old + Light_Pure)/2))
        myfile.write(Append)
        Light_Adapt_hist.append(Light_old)
        Time_Adapt_hist.append(Starting_next)
        Starting_next = Starting_next + datetime.timedelta(0, granularity)


print("Done with: " + Text + "_Adapted.txt")
