# from scipy.integrate import cumtrapz
from scipy.integrate import cumulative_trapezoid as cumtrapz
from pyproj import Geod # pip install pyproj
import time
import threading
import json

# angle_N_offset = -62.0

angle_N_offset = 83.0

#try to use gps, BNO055
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#

#from BNO055 import BNO055
from GPS import gps
from BNO055 import BNO055
#from GPS import gps

class Router:
    def __init__(self, goal_pos):#*goal_pos to goal_pos by kawako
        self.goal_flag = False
        self.goal_pos = goal_pos
        self.gps_pos = [000.0000000, 000.0000000]
        self.bno = BNO055.BNO055()
        
        # ---------------------------------------------------------
        # Initialize BNO055 and load calibration offsets
        # ---------------------------------------------------------
        if not self.bno.begin():
            print("Warning: Failed to initialize BNO055. Please check the wiring.")
        else:
            time.sleep(0.5)
            self.bno.setExternalCrystalUse(True)
            
            # Load calibration values (offsets) from the JSON file
            calib_file = "/home/cansat-stu/cansat/BNO055/bno055_calib.json"
            try:
                with open(calib_file, "r") as f:
                    offsets = json.load(f)
                
                # Write offset values to BNO055
                if self.bno.setSensorOffsets(offsets):
                    print(f"BNO055 calibration data applied! ({calib_file})")
                else:
                    print("Failed to apply BNO055 offset data.")
            
            except FileNotFoundError:
                print(f"Warning: Calibration file not found: {calib_file}")
                print("Starting in uncalibrated state.")
            except Exception as e:
                print(f"?? Error loading BNO055 calibration: {e}")
        # ---------------------------------------------------------
        
        self.geod = Geod(ellps="WGS84")
        self.azimuth = 0
        self.bwk_azimuth = 0
        self.distance = 0
        self.angle_N = 0.0
        self.start_time = time.monotonic()
        self.acc_data = [0.0]
        self.time_data = [0.0]
        self.vel = 0.0
        self.running = True
        self.longitude_flag=False
        self.latitude_flag= False

    def initialize(self):
        self.acc_data = [0]
        self.time_data = [0]
        self.start_time = time.monotonic()
        self.vel = 0

    def getGpsPos(self):
        return self.gps_pos

    def getDistance(self):
        return self.distance

    def getAzimuth(self):
        return self.azimuth

    def getVelocity(self):
        return self.vel

    def getNorth(self):
        return self.angle_N

    def getAngleDiff(self):
        return self.azimuth - self.angle_N

    def isGoal(self):
        return self.goal_flag

    def calcAngleDist(self):
        #kawako change the code like below
        lon1, lat1 = self.gps_pos[0], self.gps_pos[1]
        lon2, lat2 = self.goal_pos[0], self.goal_pos[1]
        
        #do not calculate when  GPS = ()0.0)
        if (lon1 == 0.0 and lat1 == 0.0) or (lon2 == 0.0 and lat2 == 0.0):
            print("GPS data is not updated yet, skipping angle calculation.")
            return

        self.azimuth, self.bwk_azimuth, self.distance = self.geod.inv(lon1, lat1, lon2, lat2)
        #debug output
        # print(f"GPS Position: {self.gps_pos}, Goal: {self.goal_pos}")
        # print(f"Calculated Azimuth: {self.azimuth}, Distance: {self.distance}")
        #previous code is below(by koyama)
        #c2g_pos = (self.gps_pos[0], self.gps_pos[1], self.goal_pos[0], self.goal_pos[1])
        #self.azimuth, self.bwk_azimuth, self.distance = self.geod.inv(c2g_pos)

    def checkGoal(self):
        if self.distance < 4:#10 #1
            print(f"last distance is :{self.distance}")
            self.goal_flag = True

    def update(self):
        pos = gps.getLonLat(DEG=False)
        #print(f"<update>Raw GPS Data: {pos}, Type: {type(pos)}")
        if sum(pos) != 0:
        #    #self.gps_pos = pos
        #    self.gps_pos = [pos[0] / 100.0, pos[1] / 100.0]  # make GPS value x1/100
            latitude = int(pos[1] / 100) + (pos[1] % 100.0) / 60.0
            longitude = int(pos[0] / 100) + (pos[0] % 100.0) / 60.0
            # self.gps_pos = [longitude, latitude]
             
                # Update only if latitude >= 30 and longitude >= 130
            if latitude >= 30 and longitude >= 130:
                self.gps_pos = [longitude, latitude]
                print(f"Updated GPS Position: Longitude = {longitude}, Latitude = {latitude}")
                self.calcAngleDist()  # Only update calculations if the GPS data is valid
            else:
                print(f"Invalid GPS data detected. Keeping previous values. New: Lat={latitude}, Lon={longitude}")
            
            self.calcAngleDist() #calculate angle and distance after GPS value

            print(f"latitude:{latitude}") 
            print(f"longitude:{longitude}")
            print(f"distance:{self.distance}")
        
        
        #20260228    
        #euler = self.bno.getEulerInQuat()

        euler = self.bno.getVector(self.bno.VECTOR_EULER)
        
        # 今の物理配置に合わせる
        #self.angle_N = -euler[0]
        self.angle_N = euler[0] + angle_N_offset
        
        if self.angle_N < 0:
            self.angle_N += 360
        elif self.angle_N >= 360:
            self.angle_N -= 360
            
        if self.angle_N >180:
            self.angle_N -=360
        #20260228  
        
        #~20260228  
        # self.angle_N = self.bno.getEulerInQuat()[0]
        #~20260228  
        
        # if(self.angle_N > 0):
        #     self.angle_N = 180 - self.angle_N
        # else:
        #     self.angle_N = 180 + self.angle_N 

        print("angle_N in update=",self.angle_N)

        #Check Later
        accy = self.bno.getVector(self.bno.VECTOR_LINEARACCEL)[1] * -1
        print(f"Acceleration Y: {accy}")  #check the value accurately

        self.acc_data.append(accy)
        timestamp = round((time.monotonic() - self.start_time) / 10, 2)
        self.time_data.append(timestamp)
        
        if len(self.acc_data) > 1:
            self.vel = cumtrapz(self.acc_data, self.time_data, initial=0)[-1]
        
        #self.calcAngleDist() move this method after gps_pos
        self.checkGoal()

    def start(self, interval= 0.05):
        self.running = True

        def run():
            while self.running:
                self.update()
                time.sleep(interval)

        thread = threading.Thread(target=run)
        thread.start()
        return thread

    def stop(self):
        self.initialize()
        self.running = False


if __name__ == "__main__":
    goal_pos = [139.870595, 35.769833]#kanamachi station_decimal(10) number(not sexagesimal(60))
    #router = Router(*goal_pos)
    router = Router(goal_pos)

    router.update()
    router.getAzimuth()
    router.getDistance()
    print("")

    router.start()

    while True:
        router.getGpsPos()
        router.getAzimuth()
        router.getDistance()
        print("")
