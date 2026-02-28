#bno055.py
import struct
import time
import math

import smbus
# 20260219 こっちの方が安定？
from smbus2 import SMBus
# 
from scipy.spatial.transform import Rotation


class BNO055:
    BNO055_ADDRESS_A = 0x28
    BNO055_ADDRESS_B = 0x29
    BNO055_ID = 0xA0

    # Power mode settings
    POWER_MODE_NORMAL = 0x00
    POWER_MODE_LOWPOWER = 0x01
    POWER_MODE_SUSPEND = 0x02

    # Operation mode settings
    OPERATION_MODE_CONFIG = 0x00
    OPERATION_MODE_ACCONLY = 0x01
    OPERATION_MODE_MAGONLY = 0x02
    OPERATION_MODE_GYRONLY = 0x03
    OPERATION_MODE_ACCMAG = 0x04
    OPERATION_MODE_ACCGYRO = 0x05
    OPERATION_MODE_MAGGYRO = 0x06
    OPERATION_MODE_AMG = 0x07
    OPERATION_MODE_IMUPLUS = 0x08
    OPERATION_MODE_COMPASS = 0x09
    OPERATION_MODE_M4G = 0x0A
    OPERATION_MODE_NDOF_FMC_OFF = 0x0B
    OPERATION_MODE_NDOF = 0x0C

    # Output vector type
    VECTOR_ACCELEROMETER = 0x08
    VECTOR_MAGNETOMETER = 0x0E
    VECTOR_GYROSCOPE = 0x14
    VECTOR_EULER = 0x1A
    VECTOR_LINEARACCEL = 0x28
    VECTOR_GRAVITY = 0x2E

    # REGISTER DEFINITION START
    BNO055_PAGE_ID_ADDR = 0x07

    BNO055_CHIP_ID_ADDR = 0x00
    BNO055_ACCEL_REV_ID_ADDR = 0x01
    BNO055_MAG_REV_ID_ADDR = 0x02
    BNO055_GYRO_REV_ID_ADDR = 0x03
    BNO055_SW_REV_ID_LSB_ADDR = 0x04
    BNO055_SW_REV_ID_MSB_ADDR = 0x05
    BNO055_BL_REV_ID_ADDR = 0x06

    # Accel data register
    BNO055_ACCEL_DATA_X_LSB_ADDR = 0x08
    BNO055_ACCEL_DATA_X_MSB_ADDR = 0x09
    BNO055_ACCEL_DATA_Y_LSB_ADDR = 0x0A
    BNO055_ACCEL_DATA_Y_MSB_ADDR = 0x0B
    BNO055_ACCEL_DATA_Z_LSB_ADDR = 0x0C
    BNO055_ACCEL_DATA_Z_MSB_ADDR = 0x0D

    # Mag data register
    BNO055_MAG_DATA_X_LSB_ADDR = 0x0E
    BNO055_MAG_DATA_X_MSB_ADDR = 0x0F
    BNO055_MAG_DATA_Y_LSB_ADDR = 0x10
    BNO055_MAG_DATA_Y_MSB_ADDR = 0x11
    BNO055_MAG_DATA_Z_LSB_ADDR = 0x12
    BNO055_MAG_DATA_Z_MSB_ADDR = 0x13

    # Gyro data registers
    BNO055_GYRO_DATA_X_LSB_ADDR = 0x14
    BNO055_GYRO_DATA_X_MSB_ADDR = 0x15
    BNO055_GYRO_DATA_Y_LSB_ADDR = 0x16
    BNO055_GYRO_DATA_Y_MSB_ADDR = 0x17
    BNO055_GYRO_DATA_Z_LSB_ADDR = 0x18
    BNO055_GYRO_DATA_Z_MSB_ADDR = 0x19

    # Euler data registers
    BNO055_EULER_H_LSB_ADDR = 0x1A
    BNO055_EULER_H_MSB_ADDR = 0x1B
    BNO055_EULER_R_LSB_ADDR = 0x1C
    BNO055_EULER_R_MSB_ADDR = 0x1D
    BNO055_EULER_P_LSB_ADDR = 0x1E
    BNO055_EULER_P_MSB_ADDR = 0x1F

    # Quaternion data registers
    BNO055_QUATERNION_DATA_W_LSB_ADDR = 0x20
    BNO055_QUATERNION_DATA_W_MSB_ADDR = 0x21
    BNO055_QUATERNION_DATA_X_LSB_ADDR = 0x22
    BNO055_QUATERNION_DATA_X_MSB_ADDR = 0x23
    BNO055_QUATERNION_DATA_Y_LSB_ADDR = 0x24
    BNO055_QUATERNION_DATA_Y_MSB_ADDR = 0x25
    BNO055_QUATERNION_DATA_Z_LSB_ADDR = 0x26
    BNO055_QUATERNION_DATA_Z_MSB_ADDR = 0x27

    # Linear acceleration data registers
    BNO055_LINEAR_ACCEL_DATA_X_LSB_ADDR = 0x28
    BNO055_LINEAR_ACCEL_DATA_X_MSB_ADDR = 0x29
    BNO055_LINEAR_ACCEL_DATA_Y_LSB_ADDR = 0x2A
    BNO055_LINEAR_ACCEL_DATA_Y_MSB_ADDR = 0x2B
    BNO055_LINEAR_ACCEL_DATA_Z_LSB_ADDR = 0x2C
    BNO055_LINEAR_ACCEL_DATA_Z_MSB_ADDR = 0x2D

    # Gravity data registers
    BNO055_GRAVITY_DATA_X_LSB_ADDR = 0x2E
    BNO055_GRAVITY_DATA_X_MSB_ADDR = 0x2F
    BNO055_GRAVITY_DATA_Y_LSB_ADDR = 0x30
    BNO055_GRAVITY_DATA_Y_MSB_ADDR = 0x31
    BNO055_GRAVITY_DATA_Z_LSB_ADDR = 0x32
    BNO055_GRAVITY_DATA_Z_MSB_ADDR = 0x33

    # Temperature data register
    BNO055_TEMP_ADDR = 0x34

    # Status registers
    BNO055_CALIB_STAT_ADDR = 0x35
    BNO055_SELFTEST_RESULT_ADDR = 0x36
    BNO055_INTR_STAT_ADDR = 0x37

    BNO055_SYS_CLK_STAT_ADDR = 0x38
    BNO055_SYS_STAT_ADDR = 0x39
    BNO055_SYS_ERR_ADDR = 0x3A

    # Unit selection register
    BNO055_UNIT_SEL_ADDR = 0x3B
    BNO055_DATA_SELECT_ADDR = 0x3C

    # Mode registers
    BNO055_OPR_MODE_ADDR = 0x3D
    BNO055_PWR_MODE_ADDR = 0x3E

    BNO055_SYS_TRIGGER_ADDR = 0x3F
    BNO055_TEMP_SOURCE_ADDR = 0x40

    # Axis remap registers
    BNO055_AXIS_MAP_CONFIG_ADDR = 0x41
    BNO055_AXIS_MAP_SIGN_ADDR = 0x42

    # SIC registers
    BNO055_SIC_MATRIX_0_LSB_ADDR = 0x43
    BNO055_SIC_MATRIX_0_MSB_ADDR = 0x44
    BNO055_SIC_MATRIX_1_LSB_ADDR = 0x45
    BNO055_SIC_MATRIX_1_MSB_ADDR = 0x46
    BNO055_SIC_MATRIX_2_LSB_ADDR = 0x47
    BNO055_SIC_MATRIX_2_MSB_ADDR = 0x48
    BNO055_SIC_MATRIX_3_LSB_ADDR = 0x49
    BNO055_SIC_MATRIX_3_MSB_ADDR = 0x4A
    BNO055_SIC_MATRIX_4_LSB_ADDR = 0x4B
    BNO055_SIC_MATRIX_4_MSB_ADDR = 0x4C
    BNO055_SIC_MATRIX_5_LSB_ADDR = 0x4D
    BNO055_SIC_MATRIX_5_MSB_ADDR = 0x4E
    BNO055_SIC_MATRIX_6_LSB_ADDR = 0x4F
    BNO055_SIC_MATRIX_6_MSB_ADDR = 0x50
    BNO055_SIC_MATRIX_7_LSB_ADDR = 0x51
    BNO055_SIC_MATRIX_7_MSB_ADDR = 0x52
    BNO055_SIC_MATRIX_8_LSB_ADDR = 0x53
    BNO055_SIC_MATRIX_8_MSB_ADDR = 0x54

    # Accelerometer Offset registers
    ACCEL_OFFSET_X_LSB_ADDR = 0x55
    ACCEL_OFFSET_X_MSB_ADDR = 0x56
    ACCEL_OFFSET_Y_LSB_ADDR = 0x57
    ACCEL_OFFSET_Y_MSB_ADDR = 0x58
    ACCEL_OFFSET_Z_LSB_ADDR = 0x59
    ACCEL_OFFSET_Z_MSB_ADDR = 0x5A

    # Magnetometer Offset registers
    MAG_OFFSET_X_LSB_ADDR = 0x5B
    MAG_OFFSET_X_MSB_ADDR = 0x5C
    MAG_OFFSET_Y_LSB_ADDR = 0x5D
    MAG_OFFSET_Y_MSB_ADDR = 0x5E
    MAG_OFFSET_Z_LSB_ADDR = 0x5F
    MAG_OFFSET_Z_MSB_ADDR = 0x60

    # Gyroscope Offset registers
    GYRO_OFFSET_X_LSB_ADDR = 0x61
    GYRO_OFFSET_X_MSB_ADDR = 0x62
    GYRO_OFFSET_Y_LSB_ADDR = 0x63
    GYRO_OFFSET_Y_MSB_ADDR = 0x64
    GYRO_OFFSET_Z_LSB_ADDR = 0x65
    GYRO_OFFSET_Z_MSB_ADDR = 0x66

    # Radius registers
    ACCEL_RADIUS_LSB_ADDR = 0x67
    ACCEL_RADIUS_MSB_ADDR = 0x68
    MAG_RADIUS_LSB_ADDR = 0x69
    MAG_RADIUS_MSB_ADDR = 0x6A

    # REGISTER DEFINITION END

    # def __init__(self, sensorId=-1, address=0x28, bus_num=1):#bus_num=1 was added kawako
    #     self._sensorId = sensorId
    #     self._address = address
    #     self._mode = BNO055.OPERATION_MODE_NDOF

    #     #
    #     self._bus = smbus.SMBus(bus_num)#Initilization of I2C bus added by kawako
    #     #
    
    # added by kawako 20260219
    def __init__(self, sensorId=-1, address=0x28, bus_num=1):
        self._sensorId = sensorId
        self._address = address
        self._mode = BNO055.OPERATION_MODE_NDOF
        self._bus = SMBus(bus_num)
    # 

    # def begin(self, mode=None):
    #     if mode is None:
    #         mode = BNO055.OPERATION_MODE_NDOF
    #     # Open I2C bus
    #     self._bus = smbus.SMBus(1)

    #     # Make sure we have the right device
    #     if self.readBytes(BNO055.BNO055_CHIP_ID_ADDR)[0] != BNO055.BNO055_ID:
    #         # Wait for the device to boot up
    #         time.sleep(1)
    #         if self.readBytes(BNO055.BNO055_CHIP_ID_ADDR)[0] != BNO055.BNO055_ID:
    #             return False

    #     # Switch to config mode
    #     self.setMode(BNO055.OPERATION_MODE_CONFIG)

    #     # Trigger a reset and wait for the device to boot up again
    #     self.writeBytes(BNO055.BNO055_SYS_TRIGGER_ADDR, [0x20])
    #     time.sleep(1)
    #     while self.readBytes(BNO055.BNO055_CHIP_ID_ADDR)[0] != BNO055.BNO055_ID:
    #         time.sleep(0.01)
    #     time.sleep(0.05)

    #     # Set to normal power mode
    #     self.writeBytes(BNO055.BNO055_PWR_MODE_ADDR, [BNO055.POWER_MODE_NORMAL])
    #     time.sleep(0.01)

    #     self.writeBytes(BNO055.BNO055_PAGE_ID_ADDR, [0])
    #     self.writeBytes(BNO055.BNO055_SYS_TRIGGER_ADDR, [0])
    #     time.sleep(0.01)

    #     # Set the requested mode
    #     self.setMode(mode)
    #     time.sleep(0.02)

    #     return True
    
    # added by kawako 20260219
    def begin(self, mode=None):
        if mode is None:
            mode = BNO055.OPERATION_MODE_NDOF

        if self.readBytes(BNO055.BNO055_CHIP_ID_ADDR)[0] != BNO055.BNO055_ID:
            time.sleep(1)
            if self.readBytes(BNO055.BNO055_CHIP_ID_ADDR)[0] != BNO055.BNO055_ID:
                return False

        self.setMode(BNO055.OPERATION_MODE_CONFIG)
        self.writeBytes(BNO055.BNO055_SYS_TRIGGER_ADDR, [0x20])
        time.sleep(1)

        while self.readBytes(BNO055.BNO055_CHIP_ID_ADDR)[0] != BNO055.BNO055_ID:
            time.sleep(0.01)

        self.writeBytes(BNO055.BNO055_PWR_MODE_ADDR, [BNO055.POWER_MODE_NORMAL])
        time.sleep(0.01)

        self.setMode(mode)
        time.sleep(0.02)

        self.setExternalCrystalUse(True)

        return True

    def setMode(self, mode):
        self._mode = mode
        self.writeBytes(BNO055.BNO055_OPR_MODE_ADDR, [self._mode])
        time.sleep(0.03)

    def setExternalCrystalUse(self, useExternalCrystal=True):
        prevMode = self._mode
        self.setMode(BNO055.OPERATION_MODE_CONFIG)
        time.sleep(0.025)
        self.writeBytes(BNO055.BNO055_PAGE_ID_ADDR, [0])
        self.writeBytes(
            BNO055.BNO055_SYS_TRIGGER_ADDR, [0x80] if useExternalCrystal else [0]
        )
        time.sleep(0.01)
        self.setMode(prevMode)
        time.sleep(0.02)

    def getSystemStatus(self):
        self.writeBytes(BNO055.BNO055_PAGE_ID_ADDR, [0])
        (sys_stat, sys_err) = self.readBytes(BNO055.BNO055_SYS_STAT_ADDR, 2)
        self_test = self.readBytes(BNO055.BNO055_SELFTEST_RESULT_ADDR)[0]
        return (sys_stat, self_test, sys_err)

    def getRevInfo(self):
        (accel_rev, mag_rev, gyro_rev) = self.readBytes(
            BNO055.BNO055_ACCEL_REV_ID_ADDR, 3
        )
        sw_rev = self.readBytes(BNO055.BNO055_SW_REV_ID_LSB_ADDR, 2)
        sw_rev = sw_rev[0] | sw_rev[1] << 8
        bl_rev = self.readBytes(BNO055.BNO055_BL_REV_ID_ADDR)[0]
        return (accel_rev, mag_rev, gyro_rev, sw_rev, bl_rev)

    def getCalibration(self):
        calData = self.readBytes(BNO055.BNO055_CALIB_STAT_ADDR)[0]
        return (
            calData >> 6 & 0x03,
            calData >> 4 & 0x03,
            calData >> 2 & 0x03,
            calData & 0x03,
        )
        
    def getSensorOffsets(self):
        prevMode = self._mode
        self.setMode(BNO055.OPERATION_MODE_CONFIG)
        time.sleep(0.025)
        offsets = self.readBytes(BNO055.ACCEL_OFFSET_X_LSB_ADDR, 22)
        self.setMode(prevMode)
        return offsets

    def setSensorOffsets(self, offset_list):
        if len(offset_list) != 22:
            print("Error: sizes of offsets data is not correct")
            return False
            
        prevMode = self._mode
        self.setMode(BNO055.OPERATION_MODE_CONFIG)
        time.sleep(0.025)
        self.writeBytes(BNO055.ACCEL_OFFSET_X_LSB_ADDR, offset_list)
        self.setMode(prevMode)
        return True


    def getTemp(self):
        return self.readBytes(BNO055.BNO055_TEMP_ADDR)[0]

    def getVector(self, vectorType):
        buf = self.readBytes(vectorType, 6)
        xyz = struct.unpack(
            "hhh", struct.pack("BBBBBB", buf[0], buf[1], buf[2], buf[3], buf[4], buf[5])
        )
        if vectorType == BNO055.VECTOR_MAGNETOMETER:
            scalingFactor = 16.0
        elif vectorType == BNO055.VECTOR_GYROSCOPE:
            scalingFactor = 900.0
        elif vectorType == BNO055.VECTOR_EULER:
            scalingFactor = 16.0
        elif vectorType == BNO055.VECTOR_GRAVITY:
            scalingFactor = 100.0
        else:
            scalingFactor = 1.0
        return tuple([i / scalingFactor for i in xyz])

    def getQuat(self):
        buf = self.readBytes(BNO055.BNO055_QUATERNION_DATA_W_LSB_ADDR, 8)
        wxyz = struct.unpack(
            "hhhh",
            struct.pack(
                "BBBBBBBB",
                buf[0],
                buf[1],
                buf[2],
                buf[3],
                buf[4],
                buf[5],
                buf[6],
                buf[7],
            ),
        )
        return tuple([i * (1.0 / (1 << 14)) for i in wxyz])

    def readBytes(self, register, numBytes=1):
        return self._bus.read_i2c_block_data(self._address, register, numBytes)

    def writeBytes(self, register, byteVals):
        return self._bus.write_i2c_block_data(self._address, register, byteVals)

    # def getEulerInQuat(self):
    #     quat = bno.getQuat()
    #     if quat != (0, 0, 0, 0):
    #         rot = Rotation.from_quat(quat)
    #         euler_angles = rot.as_euler("xyz", degrees=True)
    #         return euler_angles
    #     else:
    #         return (0, 0, 0, 0)
    
    # added by kawako 20260219
    def getEulerInQuat(self):
        quat = self.getQuat()
        if quat != (0, 0, 0, 0):
            rot = Rotation.from_quat(quat)
            return rot.as_euler("xyz", degrees=True)
        return (0, 0, 0)

    # Decide later
    def getABSAccelaration(self):
        acc = self.getVector(BNO055.VECTOR_LINEARACCEL)
        abs_acc = math.sqrt(acc[0] ** 2 + acc[1] ** 2 + acc[2] ** 2)
        return abs_acc

    # def getABSVelocity(self, time_span):
    #     global g_vel = 0
    #     global g_oldacc = 0
    #     lowpass_value = 0
    #     filter_cofficient = 0.9
    #     acc = self.getABSAccelaration()
    #     lowpass_value = lowpass_value * filter_cofficient + acc * (1 - filter_cofficient)
    #     g_vel = (lowpass_value + g_oldacc) * time_span + g_vel

    def recordLog(self):
        date = time.strftime("%H:%M:%S.%f")
        path = "./BNO055.log"

        bufE = self.getEulerInQuat()
        bufA = self.getVector(BNO055.VECTOR_LINEARACCEL)
        try:
            with open(path, "x", encoding="utf-8") as f:
                print(
                    "%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f"
                    % (date, bufE[0], bufE[1], bufE[2], bufA[0], bufA[1], bufA[2]),
                    file=f,
                )
        except:
            with open(path, "a", encoding="utf-8") as f:
                print(
                    "%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f"
                    % (date, bufE[0], bufE[1], bufE[2], bufA[0], bufA[1], bufA[2]),
                    file=f,
                )


if __name__ == "__main__":
    bno = BNO055()
    if bno.begin() is not True:
        print("Error initializing device")
        exit()
    time.sleep(1)
    bno.setExternalCrystalUse(True)
    
    print(f"Calibration start! Move the sensor!")
    
    

    while True:
        euler = bno.getEulerInQuat()
        acc = bno.getVector(BNO055.VECTOR_LINEARACCEL)
        print(bno.getCalibration())
        print(f"Euler x y z[deg]: {bno.getEulerInQuat()}")
        print(
            f"Acc x y z[m/s]: {bno.getVector(BNO055.VECTOR_LINEARACCEL)}" 
        )
        print(f"Acc[m/s]: %.2f" % bno.getABSAccelaration())
        bno.recordLog()
        time.sleep(0.1)
