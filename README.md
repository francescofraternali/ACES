# ACES: Automatic Configuration of Energy Harvesting Sensors with Reinforcement Learning

**Objective:**
ACES uses Reinforcement Learning (RL) with Q Learning to maximize environmental sensing (i.e. temperature monitoring, PIR detection events) while avoiding energy storage depletion. It has been designed for energy harvesting platforms with limited energy storage capacity (i.e. super-capacitor, capacitor, battery).

**Wireless Sensor Network Architecture:**
We target single-hop networks where a Master (Computational Unit) interacts directly with a Slave (i.e. a sensor node) to drive its sensing and collect data. The Figure below reports the wireless sensor network architecture: 

![WSN](img/Figure_1.PNG)

ACES can run in any computational unit that can converge in one day. Therefore, ACES is preferrable to be run in a base station (i.e. Raspberry PI), local server, or cloud. 

In this example, we use ACES with Pible, our custom battery-free mote for perpetual indoor BLE applications. Pible uses a solar panel to gather energy from the environment and a supercapacitor to store it. It can be used for general indoor building applications as it embeds a variety of sensors: light, temperature, humidity, PIR, reed switch, pressure, accelerometer, gyroscope, and microphone.

**How to:**
Run Main_Sim.py to start ACES. The system will initially look for an existing Q-Table inside the folder Q_tables. If not found, it will calculate a new Q_Table from scratch. 

To learn a new Q-Table ACES requires the last day of lighting levels in lux. If those are not present, the system will automatically use all "0" lighting levels.

In "ID_RL.txt" put the name of your experiment and after the comma put the input state of the RL separated by '|'. By default, ACES uses the following observations: the supercapacitor voltage level (i.e. SC_norm), light (i.e. Light) and week/weekend day (i.e. week). Remove one or more observations to check how ACES behaves while having less inputs to learn from.

Enjoy!
