#!/usr/bin/python

import sys

def main():
	raw_temp_data = sys.argv[1]	# Start with raw data from SensorTag
	raw_temp_bytes = raw_temp_data.split() # Split into individual bytes
	batt_percent = int(raw_temp_bytes[2], 16)
	performance = int(raw_temp_bytes[1], 16)
        reed = int(raw_temp_bytes[0], 16)
	PIR_Out = int(raw_temp_bytes[5], 16)
	light_2 = int(raw_temp_bytes[3], 16)
	light_1 = int(raw_temp_bytes[4], 16)
	light = (light_1 << 8) | (light_2);
	#light = light*4  # if you use an external case
	light = light
	print str(performance)+"|"+str(batt_percent)+"|"+str(PIR_Out)+"|"+str(reed)+"|"+str(light)+"|perf-batt-PIR-reed-light"
	
main()

