#!/usr/bin/python
import ms5837
import time

sensor = ms5837.MS5837_30BA() # Default I2C bus is 1 (Raspberry Pi 3)

# We must initialize the sensor before reading it
if not sensor.init():
        print("Sensor could6666 not be initialized")
        
# We have to read values from sensor to update pressure and temperature
if not sensor.read():
    print("Sensor read failed!")
    


freshwaterDepth = sensor.depth() # default is freshwater
sensor.setFluidDensity(ms5837.DENSITY_SALTWATER)
saltwaterDepth = sensor.depth() # No nead to read() again
sensor.setFluidDensity(1000) # kg/m^3
print(freshwaterDepth, saltwaterDepth)

print(sensor.altitude()) # relative to Mean Sea Level pressure in air

time.sleep(1)

mass_data_cor_depth = []
for i in range(500):
    mass_data_cor_depth.append(sensor.depth())
depth_corr = sum(mass_data_cor_depth) / 500


def req_depth():
    mass = []
    for i in range(200):
        mass.append(round(sensor.depth() - depth_corr, 3))
    return round(sum(mass) / 200, 3)


while True:
        if sensor.read():
                print(req_depth()) 
        else:
                print("Sensor read failed!")
                exit(1)
        time.sleep(0.5)


