import smbus
import time
import pynmea2

I2C_BUS = 1
GPS_ADDRESS = 0x42

# SMBusオブジェクトの作成
bus = smbus.SMBus(I2C_BUS)


# 緯度,経度,時間をlogファイルに上書きする
def recordLog():
    read_lon, read_lat, read_time = get_lon_lat_time()
    date = time.strftime("%H:%M:%S.%f")
    path = "./GPS.log"

    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{date},{read_lon},{read_lat},{read_time}\n")

    except:
        with open(path, "x", encoding="utf-8") as f:
            f.write(f"{date},{read_lon},{read_lat},{read_time}\n")


def proccess_data_gps(data_nmea):
    # 行でsplit
    data_nmea_arr = data_nmea.split("\r\n")
    # GPSが取得できない場合はこの値を返す
    read_lon = "00000.00000"
    read_lat = "00000.00000"
    read_time = "00:00:00+00:00"

    for index_i in range(len(data_nmea_arr)):
        # print(data_nmea_arr[index_i], end=" ")
        start_index = data_nmea_arr[index_i].find("$") + 3
        end_index = data_nmea_arr[index_i].find(",")
        nmea_cat = data_nmea_arr[index_i][start_index:end_index]
        # print("nmea_cat:",nmea_cat,end="")
        if nmea_cat == "RMC" or nmea_cat == "GGA" or nmea_cat == "GLL":
            try:
                # print("nmea_cat:",nmea_cat,end=", ")
                msg = pynmea2.parse(data_nmea_arr[index_i])
                # print("longitude:",msg.lon,", latitude:", msg.lat)
                
                # 昔
                read_lon = msg.lon
                read_lat = msg.lat
                
                #今(あってるか？20260228）
                # read_lon = msg.longitude
                # read_lat = msg.latitude
            except Exception as e:
                print("", end="")
        # else:
        # print("<-not include lon,lat")
        if nmea_cat == "GLL":
            try:
                # print("nmea_cat:",nmea_cat,end=", ")
                msg = pynmea2.parse(data_nmea_arr[index_i])
                # print("timestamp:",msg.timestamp)
                read_time = msg.timestamp
            except Exception as e:
                print("", end="")
    return read_lon, read_lat, read_time


def read_data_gps():
    try:
        rx_data_nmea = ""
        check = 0
        count_FF = 0
        while check == 0:
            rx_data = bus.read_i2c_block_data(GPS_ADDRESS, 0xFF, 16)

            for byte in rx_data:
                if byte != 0xFF:
                    rx_data_nmea += chr(byte)
                    count_FF = 0
                else:
                    count_FF += 1
                    # print(count_FF, len(rx_data_nmea))
                    if count_FF >= 50 and len(rx_data_nmea) >= 1:
                        # print("NoData Period")
                        count_FF = 0
                        check = 1

        return rx_data_nmea

    except Exception as e:
        print("", end="")
        # print(f"Error reading from GPS module: {e}")
        return ""


def get_lon_lat_time():
    rx_data_nmea = read_data_gps()
    # print("RAW DATA:", rx_data_nmea)   # ←追加
    read_lon, read_lat, read_time = proccess_data_gps(rx_data_nmea)
    # attempt = 0

    # while (read_lon == "00000.00000" or read_lat == "00000.00000") and attempt < 10:
    #     attempt += 1
    #     if attempt == 1:
    #         print("GPS data not found. Retrying...", end="")
    #     print(attempt, end=",")
    #     rx_data_nmea = read_data_gps()
    #     read_lon, read_lat, read_time = proccess_data_gps(rx_data_nmea)
    #     time.sleep(0.5)
    # print("")
    return read_lon, read_lat, read_time

def getLonLat(DEG=True):
    read_lon, read_lat, read_time = get_lon_lat_time()

    if read_lon in ("00000.00000", None) or read_lat in ("00000.00000", None):
        return [0.0, 0.0]

    try:
        lon = float(read_lon)
        lat = float(read_lat)
    except:
        return [0.0, 0.0]

    return [lon, lat]


# while True:
#     read_lon, read_lat, read_time = get_lon_lat_time()
#     recordLog()
#     print("Longitude:", read_lon, ", Latitude:", read_lat, ", Time:", read_time)
#     time.sleep(3)

if __name__ == "__main__":
    while True:
        read_lon, read_lat, read_time = get_lon_lat_time()
        recordLog()
        print("Longitude:", read_lon, ", Latitude:", read_lat, ", Time:", read_time)
        time.sleep(3)