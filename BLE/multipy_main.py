import sys
import subprocess
from time import sleep
import json
import os
import time
import datetime
from subprocess import PIPE

path = '/home/pi/BLE_GIT/Base_Station/'
ID_List = []
Name_List = []
File_List = []

Name_spl = []
File_spl = []

with open("../ID_BLE.txt", "r") as f:
    for line in f:
        splitted = line.split(',')
        print(splitted)
        Name_spl.append(splitted[0]) 
        File_spl.append(splitted[1]) 
#print(Name_spl, File_spl)

if len(Name_spl) == len(File_spl):
    print("File Ok Ok")
else:
    print("Error: Check ID File")
    quit()

dict_dev = {}

with open('pible_dev_list.txt', 'r') as inf:
    for data in inf:
        line = data.strip().split(' ')
        dict_dev[line[0]] = line[1]

for i in range(len(File_spl)):
    checker = 1
    for key, val in dict_dev.items():
        if Name_spl[i] == val:
            ID_List.append(key)
            checker = 0
            break
    if checker == 1:
        print('Huston we have a problem, sensor not found! Try updating device List!')
        quit()
    Name_List.append(str(Name_spl[i])) #["Sensor_5", "Sensor_1"]
    File_List.append('../Data/' + str(File_spl[i])) #["2142_Middle_Battery.txt", "2142_Middle_Pible.txt"]

#print(ID_List)
#print(Name_List)
#print(File_List)
#quit()

#finder_time = 3 # time needed to avoid that multiple process are called and not completly killed. Put 3 for one sensor and 1 for several sensors
write_completed = 1 #after you write a data you avoid to call the sensor again. 
tryals = 5 #number of trials it looks for a specific device. Each try is 0.5s. 

def kill_search():
	subprocess.Popen("killall Find_New_BLE_Device.sh 2>/dev/null", shell=True)

def killer():
	subprocess.Popen("killall Detector.sh 2>/dev/null", shell=True)
	subprocess.Popen("killall gatttool 2>/dev/null" , shell=True)

def check():
    for ii in range(0,tryals):
        with open('wait.txt', 'r') as f:
            first_line = f.readline()
        first = first_line[:1]
        #print(first)
        if first == '2': # if it reads 2 that means that Detector.sh has already written everything
	    #print "Sleep 1"
            sleep(write_completed)
            return
        if first == '1': #if it reads 1 it we five him other 10 extra seconds to finish to write the data
            for i in range(0,10):
                #print('here')
                with open('wait.txt', 'r') as f:
                    first_line = f.readline()
			
                first = first_line[:1]
                if first == '2':
                    sleep(write_completed)
                    return
                sleep(0.5)
        sleep(0.5)

def get_raw_data(ID):
    with open('wait.txt', 'w') as f:
        f.write('0')
        sleep(0.1)
                    
    for i in range(len(ID_List)):
        if ID == ID_List[i]:
            Name = Name_List[i]
            File = File_List[i]
            break

    with open('ID.txt', 'r') as f:
        Action = '-1'
        for line in f:
            line = line.strip()
            splt = line.split(',')
            if Name == splt[0]:
                #print(splt[0], splt[2])
                Action = splt[2]
                break
        
        if Action == '-1':
            print("Pay Attention: Name and Action not found")
            Action = '0'

    #print("bash get_data_from_device.sh "+Name+" "+ID+" "+File+" "+Action) 
    subprocess.Popen("bash get_data_from_device.sh "+Name+" "+ID+" "+File+" "+Action+" &", shell=True)
   
    #subprocess.Popen('bash get_data_from_device.sh ' +Name+' '+ID+' '+File+' '+Action+' &', shell=True)
    #print('checking')
    check()
    #print('checking over')
    killer()
    sleep(0.5)
                    
def get_action_name(ID):
    for i in range(len(ID_List)):
        if ID == ID_List[i]:
            Name = Name_List[i]
            File = File_List[i]
            break

    with open('../ID/ID.txt', 'r') as f:
        Action = '-1'
        for line in f:
            line = line.strip()
            splt = line.split(',')
            if Name == splt[0]:
                #print(splt[0], splt[2])
                Action = splt[2]
                break
    return (Action, Name, File)
     

def check_reboot():
    proc = subprocess.Popen("cat /var/log/auth.log | grep 'Accepted password' > Accepted_file.txt", stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
	
    for line in reversed(open('Accepted_file.txt').readlines()):
        #print(line.rstrip())
        spl = line.rstrip()
        spl = spl.split(' ')
        if 'Accepted' in spl and spl[1].isdigit():
            break
	
    print(spl)
    clock = spl[2].split(':')
	
    now = datetime.datetime.now()
    now_time = now.strftime('%m/%d/%y %H:%M:%S')

    month = datetime.datetime.strptime(spl[0], '%b')
    last_bs_read_time = datetime.datetime(int(now.year), int(month.month), int(spl[1]), int(clock[0]), int(clock[1]), int(clock[2]))
    if os.path.isfile('last_reset.txt'):
        with open('last_reset.txt', 'r') as f:
            out = f.readlines()
        last_reset = datetime.datetime.strptime(out[0], '%m/%d/%y %H:%M:%S')
        #print("file exists", now_last)
    else:
        with open('last_reset.txt', 'w') as f:
            f.write(now_time)
        print("File does not exist. Creating it", now)
        last_reset = now
	
    diff_1 = (now - last_bs_read_time).total_seconds()
    diff_2 = (now - last_reset).total_seconds()
    
    print(str(int(diff_1)) + "/3600, " + str(int(diff_2)) + "/14400")
    if diff_1 > 60*60*1:  # if nobody is reading into the BS for diff_1 time then I put all actions to 0 to avoid node dying
        action_imposed = 0
        print("action imposed to 0 since bs in not reading data")
        if diff_2 > 60*60*4:  # if nobody is writing for diff_1 time and the BS was one for one day, then reboot
            with open('last_reset.txt', 'w') as f:
                f.write(now_time)
            sleep(1)
            print("Nobody wants me. Or maybe I am broken? Reeboting...")
            subprocess.Popen("sudo reboot", shell=True)
    else:
         action_imposed = -1

    return action_imposed
	
print("Let us Start!!")

#Reset BLE drivers
#subprocess.Popen("sudo hciconfig hci0 reset &", shell=True)
#print(json.dumps(dict_dev, indent=1, sort_keys=True))

avoid = []  # in this list there are all the devices that have been read and that needs to be left alone for a bit to avoid to get the data read twice.
countarell = 360
count_empty = 0
action_imposed = -1

while(True):
    #print('here')	
    Name = ''
    File = ''
    #print("scanning")
    try:
    	os.remove('dev_found.txt')
    except:
        pass
    #subprocess.Popen("bash Find_New_BLE_Device.sh > dev_found.txt", shell=True)
    subprocess.Popen('sudo blescan -t 3 > dev_found.txt 2> ble_err.txt', shell=True)
    sleep(3.5)
    found = []
    if (os.stat('dev_found.txt').st_size < 2) or (os.stat('ble_err.txt').st_size > 1):
        print('dev_found empty or blescan error')
        print('blescan stderr file dimension:', os.stat('ble_err.txt').st_size)
        sleep(5)
        if count_empty >= 10:
            print('List Empty. No devices found for a while. Rebooting BS.')
            subprocess.Popen('sudo reboot', shell=True)
            sleep(5)
        else:
            print('List Empty. No devices found, something wrong? Resetting BLE hci0 adapter')
            subprocess.Popen('sudo hciconfig hci0 reset', shell=True)
            count_empty += 1
    else:
        count_empty = 0
        with open("dev_found.txt", 'r') as f:
            for line in f:
                line = line.strip()
                #print(len(line))
                splitted = line.split(' ')
                try:
                    ID = splitted[2][5:22]
                except:
                    ID = 'Not_found'
                if ID in ID_List and ID not in avoid and ID not in found:
                        #print('trovato')
                        found.append(ID)
                        Action, Name, File = get_action_name(ID)
                        log_temp = File.split('/')
                        log = log_temp[-1]
                    
                        t = time.strftime('%m/%d/%y %H:%M:%S')
			
                        if action_imposed == 0:
                            Action = '0'
                        subprocess.Popen("bash Detector.sh " + Name + " " + ID + " " + File + " " + Action + " " + log + " 2>error.txt &", shell=True)


    #print("found", found)
    if len(avoid) > 0:
        #print('remove avoiding last ID')
        for ID in ID_List:
            if ID in avoid: 
                avoid.remove(ID)
                #print('removing ', ID)

    if len(found) > 0:   # There are some device that needs to be downloaded
        for ID in found:
            avoid.append(ID)
            avoid.append(ID)
            avoid.append(ID)
            #avoid.append(ID)
            #print('avoiding ', ID)
        
       
    #if len(found) > 0:
    #    #for i in range(len(ID_List)):
    #    avoid.append(found[-1])
    #    avoid.append(found[-1])
        #print('avoiding last ID')
    try:
    	with open('error.txt','r') as f:
            for line in f:
	        #print(line)
                contain = line.strip().split(' ')
                if (len(line.strip()) > 0) and '(38)' not in contain and '(107)' not in contain and '(111)' not in contain and 'unlikely' not in contain and 'Traceback' not in contain:
                    print(line)
                    print('something wrong, resetting')
                    sleep(5)
                    os.remove('error.txt')
                    subprocess.Popen('sudo hciconfig hci0 reset', shell=True)
                    sleep(5)
                    break
    except:
        continue

    sleep(1)
    countarell += 1
    if countarell >= 360: # Use 360 as default that is 60*30/5 sec
        try:
            print("checking reboot")
            action_imposed = check_reboot()
        except Exception as e: print("something wrong in check_reboot with error: ", e)
        countarell = 0
        sleep(1)
print("It's Over")

#sudo hciconfig hci0 reset

#B0:B4:48:C9:EA:83
#gatttool -b $Sensor --char-write-req -a 0x0024 -n 00

#subprocess.Popen("gatttool -b B0:B4:48:C9:EA:83 --char-write-req -a 0x0024 -n 00")
