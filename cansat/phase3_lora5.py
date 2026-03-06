# from Router import router2 as router
# from LoRa import lora_tx_release_pre4 as LoRaTX
# from Motor import robot
# import time
# import csv
# import threading

# robot.initialize()

# def phase3(goal_pos, PORT, BAUDRATE, RESET_PIN, GPS_FILE_PATH, SENTDATA_LOG_FILE_PATH):

#     rt = router.Router(goal_pos)
#     log_file = "test_log_mayu.csv"

#     tx = LoRaTX.LoRaTransmitter(
#         PORT,
#         BAUDRATE,
#         RESET_PIN,
#         GPS_FILE_PATH,
#         SENTDATA_LOG_FILE_PATH
#     )

#     tx.initialize_device()

#     # =========================
#     # LoRa送信スレッド
#     # =========================

#     def lora_thread():
#         tx.run()

#     lora_thread_obj = threading.Thread(target=lora_thread)
#     lora_thread_obj.start()

#     # =========================
#     # ★ phase3開始マーカー送信
#     # =========================

#     tx.send_marker("33333.00000", "33333.00000")

#     # =========================
#     # CSVログ作成
#     # =========================

#     with open(log_file, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([
#             "Timestamp",
#             "Latitude",
#             "Longitude",
#             "Azimuth",
#             "AngleDiff",
#             "Distance",
#             "Velocity"
#         ])

#     avoidance_mode = False
#     previous_distance = float('inf')
#     distance_increase_count = 0

#     while not (rt.isGoal() and rt.longitude_flag == True and rt.latitude_flag == True):

#         times = 0

#         rt.start()
#         time.sleep(1)

#         deg = rt.getAngleDiff()
#         gps_pos = rt.getGpsPos()
#         azimuth = rt.getAzimuth()
#         distance = rt.getDistance()
#         velocity = rt.getVelocity()

#         print(f"0whilebefore turn GPS: {gps_pos}, Azimuth: {azimuth}, AngleDiff: {deg}, Distance: {distance}, Velocity: {velocity}")

#         if gps_pos[0] == 0.0 and gps_pos[1] == 0.0:
#             print("Warning: GPS data is (0.0, 0.0)")

#         velocity_value = velocity[-1] if isinstance(velocity, list) and len(velocity) > 0 else 0.0

#         with open(log_file, mode='a', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow([
#                 time.time(),
#                 gps_pos[0],
#                 gps_pos[1],
#                 azimuth,
#                 deg,
#                 distance,
#                 velocity_value
#             ])

#         if (deg > 0):
#             if abs(deg) < abs(deg - 360):
#                 deg = deg
#             else:
#                 deg = deg - 360
#         else:
#             if abs(deg) < abs(deg + 360):
#                 deg = deg
#             else:
#                 deg = deg + 360

#         while abs(deg) > 18.0 and times < 40:

#             print("Turn!")

#             if deg > 0:
#                 robot.turn(10)
#             else:
#                 robot.turn(-10)

#             robot.stop()
#             time.sleep(1)

#             rt.update()

#             deg = rt.getAngleDiff()
#             gps_pos = rt.getGpsPos()
#             azimuth = rt.getAzimuth()
#             distance = rt.getDistance()
#             velocity = rt.getVelocity()

#             if gps_pos[0] < 130:
#                 rt.longitude_flag = False
#             else:
#                 rt.longitude_flag = True

#             if gps_pos[1] < 30:
#                 rt.latitude_flag = False
#             else:
#                 rt.latitude_flag = True

#             velocity_value = velocity[-1] if isinstance(velocity, list) and len(velocity) > 0 else 0.0

#             with open(log_file, mode='a', newline='') as file:
#                 writer = csv.writer(file)
#                 writer.writerow([
#                     time.time(),
#                     gps_pos[0],
#                     gps_pos[1],
#                     azimuth,
#                     deg,
#                     distance,
#                     velocity_value
#                 ])

#             times += 1

#         if distance > previous_distance:
#             distance_increase_count += 1
#         else:
#             distance_increase_count = 0

#         if distance_increase_count >= 5:
#             print("Entering avoidance mode...")
#             avoidance_mode = True

#         while avoidance_mode and not rt.isGoal():

#             print("Avoidance phase started")

#             initial_distance = rt.getDistance()

#             robot.move(0.75, 2)
#             time.sleep(1)

#             rt.update()

#             forward_distance = rt.getDistance()

#             if forward_distance > initial_distance:

#                 robot.turn(80)
#                 robot.move(0.75, 2)

#             robot.turn(40)

#             time.sleep(1)

#             rt.update()

#             perpendicular_distance = rt.getDistance()

#             robot.move(0.75, 2)

#             time.sleep(1)

#             rt.update()

#             new_perpendicular_distance = rt.getDistance()

#             if new_perpendicular_distance > perpendicular_distance:

#                 robot.turn(80)
#                 robot.move(0.75, 2)

#             if rt.isGoal():
#                 avoidance_mode = False

#         if not avoidance_mode:

#             if rt.isGoal():

#                 robot.move(0.75, 1)
#                 robot.stop()

#                 rt.stop()

#                 break

#             else:

#                 robot.move(0.75, 3)
#                 robot.stop()

#                 rt.stop()

#         rt.stop()

#         previous_distance = distance

#     # =========================
#     # ★ phase3終了マーカー送信
#     # =========================

#     tx.send_marker("44444.00000", "44444.00000")

#     # =========================
#     # LoRa停止
#     # =========================

#     tx.stop()

#     lora_thread_obj.join()

#     print("Arrived!!")


# if __name__ == "__main__":

#     goal_pos = [139.8615156, 35.7710006]
#     PORT = "/dev/ttyAMA0"
#     BAUDRATE = 115200
#     RESET_PIN = 25

#     #GPS_FILE_PATH = "/home/cansat-stu/log_202512/log_gps.txt"
#     #SENTDATA_LOG_FILE_PATH = "/home/cansat-stu/log_202512/sent_data_log.txt"
#     GPS_FILE_PATH = "/home/cansat-stu/cansat/phase3_log.txt"
#     SENTDATA_LOG_FILE_PATH = "/home/cansat-stu/cansat2024/Op-test_i2c/sent_data_log.txt"
#     phase3(goal_pos, PORT, BAUDRATE, RESET_PIN,
#            GPS_FILE_PATH, SENTDATA_LOG_FILE_PATH)
    
