# ACES: Automatic Configuration of Energy Harvesting Sensors with Reinforcement Learning

ACES uses Reinforcement Learning with Q Learning to maximize performance (i.e. temperature monitoring, PIR detection events) while avoiding energy storage depletion. It can be used with any energy harvesting sensor node that has some kind of energy storage (i.e. super-capacitor, capacitor, battery) so that ACES can learn energy and human patterns and adapt, the energy remaining to optimize performance.

In this example we use ACES with Pible, a battery-free mote for perpetual indoor BLE applications. Pible uses a solar panel to gather energy from the environment and a super capacitor to store it. It can be used for general indoor building applications since it is equipped with the following sensors: temperature, humidity, PIR, reed switch, pressure, accelerometer, gyroscope, microphone and light.

Run Main_Real.py to start ACES. The system will initially look for a existing Q-Table inside the folder Q_tables. IF not find it, it will start a new Q_Table from scratch. To learn a new Q-Table the system needs the last day of lighting levels in lux. If those are not present, the system will automatically uses all "0" lighting levels.
