from Router import router2 as router
import lora_tx_release_pre2 as LoRaTX
from Motor import robot
import time
import csv
import os

def phase3(goal_pos):
# def phase3(goal_pos, port, baudrate, reset_pin, file_path_lora,file_path_al):
    rt = router.Router(goal_pos)
    log_file = "test_log_mayu.csv"
    
    with open(log_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Latitude", "Longitude", "Azimuth", "AngleDiff", "Distance", "Velocity"])
    
    # rt.start()
    # time.sleep(1)
    # gps_pos = [0.0,0.0]

    avoidance_mode = False  # 回避行動モードのフラグ
    previous_distance = float('inf')  # 初回のため、最大値をセット
    ##03080544gpsのみで航法する条件となるカウント
    # 追加変数
    distance_increase_count = 0  # 連続して距離が増加した回数を記録
    ##03080544gpsのみで航法する条件となるカウント



    while not (rt.isGoal() and rt.longitude_flag==True and rt.latitude_flag==True):
        times = 0
        rt.start()
        time.sleep(1)
        
        deg = rt.getAngleDiff()
        gps_pos = rt.getGpsPos()
        azimuth = rt.getAzimuth()
        distance = rt.getDistance()
        velocity = rt.getVelocity()

        print(f"0whilebefore turn GPS: {gps_pos}, Azimuth: {azimuth}, AngleDiff: {deg}, Distance: {distance}, Velocity: {velocity}")

        # #debug 03031642 no GPS
        # start_time = time.time()
        # deg = -270
        # 
        
        # # デバッグ用出力
        # print(f"GPS: {gps_pos}, Azimuth: {azimuth}, AngleDiff: {deg}, Distance: {distance}, Velocity: {velocity}")
        
        # GPSが正しく取得されているか確認
        
        if gps_pos[0] == 0.0 and gps_pos[1] == 0.0:
            print("Warning: GPS data is (0.0, 0.0), check if GPS is working correctly.")
        
        # velocity をスカラ値に変換
        velocity_value = velocity[-1] if isinstance(velocity, list) and len(velocity) > 0 else 0.0
        
        with open(log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time.time(), gps_pos[0], gps_pos[1], azimuth, deg, distance, velocity_value])
        
        
        ##
        ##decide deg based on sign and value(add 2025/3/3)
        if (deg > 0):
            if abs(deg) < abs(deg - 360):
                # direction = "+" #use deg's sign
                deg = deg
            else:
                #direction = "-" #use (deg - 360)'s sign
                deg = deg - 360
        else: #deg < 0
            if abs(deg) < abs(deg + 360):
                #direction = "+" #use deg's sign
                deg = deg
            else:
                #direction = "-" #use (deg + 360)'s sign
                deg = deg + 360
        ##(add 2025/3/3)
        ##
        
        print("large deg")
        
        print(f"1whilebefore turn GPS: {gps_pos}, Azimuth: {azimuth}, AngleDiff: {deg}, Distance: {distance}, Velocity: {velocity}")

        #get deg from update in start() (~20250302)
        #get deg to turn from upper code (20250303~)
        while abs(deg) > 15.0 and times < 40: #5
            
            print(f"before turn GPS: {gps_pos}, Azimuth: {azimuth}, AngleDiff: {deg}, Distance: {distance}, Velocity: {velocity}")
            # rt.update()
            #robot.turn(deg/100.0)
            print("Turn!")
            # robot.turn(deg/5.0)
            
            # ##
            # if (deg > 0):
            #     if abs(deg) < abs(deg - 360):
            #         # direction = "+" #use deg's sign
            #         deg = deg
            #     else:
            #         #direction = "-" #use (deg - 360)'s sign
            #         deg = deg - 360
            # else: #deg < 0
            #     if abs(deg) < abs(deg + 360):
            #         #direction = "+" #use deg's sign
            #         deg = deg
            #     else:
            #         #direction = "-" #use (deg + 360)'s sign
            #         deg = deg + 360
            #  ##
        
            if(deg > 0):
                robot.turn(20) #
            else:
                robot.turn(-20)
            

            # ##
            # robot.turn(10)
            robot.stop()
            time.sleep(1)

            # ##030316:50 no GPS
            # if time.time() - start_time > 10:
            #     deg = 5
            # ##030316:50
            
            #debug 03031642 use these code when rover can get gps
            rt.update() #get deg from update after turn
            deg = rt.getAngleDiff()
            gps_pos = rt.getGpsPos()
            azimuth = rt.getAzimuth()
            distance = rt.getDistance()
            velocity = rt.getVelocity()
            #debug 
            #####0307
            if gps_pos[0] < 130:
                rt.longitude_flag = False
            else:
                rt.longitude_flag = True
                

            if gps_pos[1] < 30:
                rt.latitude_flag = False
            else:
                rt.latitude_flag = True
            #####               
            print(f"after turn GPS: {gps_pos}, Azimuth: {azimuth}, AngleDiff: {deg}, Distance: {distance}, Velocity: {velocity}")
            
            velocity_value = velocity[-1] if isinstance(velocity, list) and len(velocity) > 0 else 0.0
            
            with open(log_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([time.time(), gps_pos[0], gps_pos[1], azimuth, deg, distance, velocity_value])
            
            times += 1
        
        #######
        ##03080536if latest distance > previous distance for 5 times continuously
        # **回避行動モードの開始**
        # if distance > previous_distance * 1.3:
        #     print("Entering avoidance mode...")
        #     avoidance_mode = True

        # **回避行動モードの開始条件**
        if distance > previous_distance:
            distance_increase_count += 1
        else:
            distance_increase_count = 0  # 距離が減ったらカウントリセット

        if distance_increase_count >= 5:
            print("Entering avoidance mode...")
            avoidance_mode = True
        
        ####03080536

        while avoidance_mode and not rt.isGoal():
            print("Avoidance phase started")

            # **Step 1: 現在の地点の距離を取得**
            initial_distance = rt.getDistance()
            print(f"Initial Distance: {initial_distance}")

            # **Step 2: 前進して距離を取得**
            print("move")
            robot.move(0.75, 2)
            time.sleep(1)
            rt.update()
            forward_distance = rt.getDistance()
            print(f"Forward Distance: {forward_distance}")

            # **Step 3: どちらの距離が小さいかを判断**
            if forward_distance > initial_distance:
                print("Going back to previous location")
                print("turn 180 deg and move")
                robot.turn(80) #180 deg
                robot.move(0.75, 2)
            else:
                print("Staying at new location")

            # **Step 4: 90度回転して距離を取得**
            print("turn 90 deg")
            robot.turn(40) #90 deg
            time.sleep(1)
            rt.update()
            perpendicular_distance = rt.getDistance()
            print(f"Perpendicular Distance: {perpendicular_distance}")

            # **Step 5: 前進して再び距離を取得**
            print("move")
            robot.move(0.75, 2)
            time.sleep(1)
            rt.update()
            new_perpendicular_distance = rt.getDistance()
            print(f"New Perpendicular Distance: {new_perpendicular_distance}")

            # **Step 6: どちらの距離が小さいかを判断**
            if new_perpendicular_distance > perpendicular_distance:
                print("Going back to perpendicular start location")
                print("turn 180 deg and move")
                robot.turn(80) #180 deg
                robot.move(0.75, 2)
            else:
                print("Staying at new perpendicular location")

            # **ゴール判定**
            if rt.isGoal():
                print("Goal reached in avoidance mode")
                avoidance_mode = False
        ##
        ##
        # **通常モードでの移動**
        if not avoidance_mode:
            if rt.isGoal():
                print("Move and exit")
                robot.move(0.75, 1) #5
                robot.stop()
                rt.stop()
                break
            else:
                print("Move and continue")
                robot.move(0.75, 3) #5
                robot.stop()
                rt.stop()

        rt.stop()
        previous_distance = distance  # 現在の距離を保存
        ##
        ####03080536

        ##for last move 20250308 0152~

        # if rt.isGoal():
        #     print("Move and exit")
        #     robot.move(0.75, 1) #5
        #     robot.stop()
        #     rt.stop()
        # else:
        #     print("Move and continue")
        #     robot.move(0.75, 3) #5
        #     robot.stop()
        #     rt.stop()

        # ##~0308 0152
        # print("Move")
        # robot.move(0.75, 3) #5
        # robot.stop()
        # rt.stop()
        # ##~0308 0152
    
    print("Arrived!!")

if __name__ == "__main__":
    # goal_pos = [130.554131524, 30.261690416]
    # goal_pos = [130.5758851, 30.2248274]
    # goal_pos = [130.9015805, 30.41536416666667]#deg? hazi_aozora_park@tanegashima
    # goal_pos = [130.9012733, 30.41519633333333]#deg? center aozora_park@tanegashima
    goal_pos = [130.960085000, 30.374149666]#deg? contest
    # 13057.58780 , Latitude: 3022.48232 130.5758851, 30.2248274
    # goal_pos = [139.514296921, 35.461619311]
    #goal_pos = [13951.4296921, 3546.1619311]
    #goal_pos = [1.664396, 0.5961997]
    phase3(goal_pos)



# from Router import router
# from Motor import robot
# import time


# def phase3(goal_pos):
#     rt = router.Router(goal_pos)

#     while not rt.isGoal():
#         times = 0
#         rt.start()
#         time.sleep(1)
#         deg = rt.getAngleDiff()

#         while abs(deg) > 15 and times < 5:
#             robot.turn(deg)
#             deg = rt.getAngleDiff()
#             times += 1

#         robot.move(0.75, 10)
#         robot.stop()
#         rt.stop()

#     print("Arrived!!")

# if __name__ == "__main__":
#     goal_pos = [139.5182666, 35.463201]
#     phase3(goal_pos)