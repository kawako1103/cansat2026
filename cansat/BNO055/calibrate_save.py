# calibrate_save.py
import time
import json
from BNO055 import BNO055

# File name to save calibration data
CALIB_FILE = "bno055_calib.json"

def main():
    bno = BNO055()
    if not bno.begin():
        print("Failed to initialize BNO055. Please check the wiring.")
        return
        
    bno.setExternalCrystalUse(True)
    
    print("======================================================")
    print("BNO055 Step-by-Step Calibration")
    print("======================================================\n")
    
    # ---------------------------------------------------
    # Step 1: Gyroscope (Gyro)
    # ---------------------------------------------------
    print("[Step 1/3] Gyroscope Calibration")
    print("?? Place the sensor on a flat, vibration-free surface and keep it still.")
    while True:
        sys, gyro, accel, mag = bno.getCalibration()
        print(f"\rProgress -> Gyro: {gyro}/3  (Ref Sys:{sys}, Accel:{accel}, Mag:{mag})", end="")
        if gyro == 3:
            print("\n>> ? Gyroscope calibration complete!\n")
            break
        time.sleep(0.5)

    # ---------------------------------------------------
    # Step 2: Accelerometer (Accel)
    # ---------------------------------------------------
    print("[Step 2/3] Accelerometer Calibration")
    print("?? Point each of the 6 faces of the sensor downwards sequentially, pausing for about 3 seconds on each face.")
    print("  (Imagine rolling a dice and making numbers 1 to 6 face up one by one)")
    while True:
        sys, gyro, accel, mag = bno.getCalibration()
        print(f"\rProgress -> Accel: {accel}/3  (Ref Sys:{sys}, Gyro:{gyro}, Mag:{mag})", end="")
        if accel == 3:
            print("\n>> ? Accelerometer calibration complete!\n")
            break
        time.sleep(0.5)

    # ---------------------------------------------------
    # Step 3: Magnetometer (Mag)
    # ---------------------------------------------------
    print("[Step 3/3] Magnetometer Calibration")
    print("?? Move the sensor slowly in a 'figure-8' motion in the air, twisting your wrist to point it in various directions.")
    while True:
        sys, gyro, accel, mag = bno.getCalibration()
        print(f"\rProgress -> Mag: {mag}/3  (Ref Sys:{sys}, Gyro:{gyro}, Accel:{accel})", end="")
        if mag == 3:
            print("\n>> ? Magnetometer calibration complete!\n")
            break
        time.sleep(0.5)

    # ---------------------------------------------------
    # Step 4: System verification and saving
    # ---------------------------------------------------
    print("[Final Check] Waiting for overall system optimization...")
    while True:
        sys, gyro, accel, mag = bno.getCalibration()
        print(f"\rProgress -> System: {sys}/3  (Gyro:{gyro}, Accel:{accel}, Mag:{mag})", end="")
        # Proceed to saving when all reach 3
        if sys == 3 and gyro == 3 and accel == 3 and mag == 3:
            print("\n\n?? Full calibration complete!")
            
            # Get offset values
            offsets = bno.getSensorOffsets()
            
            # Write to JSON file and save
            with open(CALIB_FILE, "w") as f:
                json.dump(offsets, f)
                
            print(f"Offset values saved to '{CALIB_FILE}'.")
            print(f"Saved data: {offsets}")
            print("======================================================")
            print("Great job! You can now run the main program (phase3.py).")
            break
            
        time.sleep(0.5)

if __name__ == "__main__":
    main()