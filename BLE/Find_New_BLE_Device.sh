#To find new BLE devices:
sudo timeout -s INT 1.5s hcitool -i hci0 lescan
sleep 2.5

sudo hciconfig hci0 reset

#sudo hcitool lescan #> BLE_scan.txt
