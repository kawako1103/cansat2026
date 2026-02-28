import time
import smbus2
import math


class MS5607:

    def __init__(self, bus=1, address=0x77):
        self.bus = smbus2.SMBus(bus)
        self.address = address
        self.C = [0] * 7  # 旧コード互換用（index 1〜6使用）
        self.sea_level_pressure = 1013.25  # hPa

        try:
            self.reset()
            time.sleep(0.1)
            self.read_prom()
        except Exception as e:
            print(f"初期化エラー: {e}")

    def reset(self):
        self.bus.write_byte(self.address, 0x1E)

    def read_prom(self):
        for i in range(1, 7):
            cmd = 0xA0 + (i * 2)
            data = self.bus.read_i2c_block_data(self.address, cmd, 2)
            self.C[i] = (data[0] << 8) + data[1]

    def read_adc(self, cmd):
        self.bus.write_byte(self.address, cmd)
        time.sleep(0.01)
        data = self.bus.read_i2c_block_data(self.address, 0x00, 3)
        return (data[0] << 16) + (data[1] << 8) + data[2]

    def read_data(self):

        D1 = self.read_adc(0x48)  # Pressure
        D2 = self.read_adc(0x58)  # Temp

        dT = D2 - (self.C[5] * 256)
        TEMP = 2000 + (dT * self.C[6] / 8388608)

        OFF = (self.C[2] * 131072) + ((self.C[4] * dT) / 64)
        SENS = (self.C[1] * 65536) + ((self.C[3] * dT) / 128)

        if TEMP < 2000:
            T2 = (dT * dT) / 2147483648
            OFF2 = 5 * ((TEMP - 2000) ** 2) / 2
            SENS2 = 5 * ((TEMP - 2000) ** 2) / 4

            if TEMP < -1500:
                OFF2 += 7 * ((TEMP + 1500) ** 2)
                SENS2 += 11 * ((TEMP + 1500) ** 2) / 2

            TEMP -= T2
            OFF -= OFF2
            SENS -= SENS2

        P = (D1 * SENS / 2097152 - OFF) / 32768

        pressure_hPa = P / 100.0
        temperature_c = TEMP / 100.0

        return pressure_hPa, temperature_c

    # ===== 旧コード互換：引数なしで高度取得 =====
    def getAltitude(self):
        pressure, _ = self.read_data()
        altitude = 44330.0 * (
            1.0 - math.pow(pressure / self.sea_level_pressure, 0.1903)
        )
        return altitude

    # 旧関数名も残す（両対応）
    def get_altitude(self, pressure, sea_level_pressure=1013.25):
        altitude = 44330.0 * (
            1.0 - math.pow(pressure / sea_level_pressure, 0.1903)
        )
        return altitude


# --- テスト ---
if __name__ == "__main__":

    sensor = MS5607(address=0x77)

    print("MS5607 Altimeter Reading...")
    print("-" * 30)

    try:
        while True:
            press, temp = sensor.read_data()
            alt = sensor.getAltitude()  # ← 旧コード互換動作

            print(f"気圧: {press:.2f} hPa | 温度: {temp:.2f} °C | 推定高度: {alt:.2f} m")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n停止しました")

# import time
# import smbus2
# import math

# class MS5607:
#     def __init__(self, bus=1, address=0x77):
#         self.bus = smbus2.SMBus(bus)
#         self.address = address
#         self.C = [] # 補正係数格納用
        
#         try:
#             self.reset()
#             time.sleep(0.1)
#             self.read_prom()
#         except Exception as e:
#             print(f"初期化エラー: {e}")

#     def reset(self):
#         # リセットコマンド
#         self.bus.write_byte(self.address, 0x1E)

#     def read_prom(self):
#         # 補正係数(C1〜C6)を読み込む
#         # コマンド 0xA0 〜 0xAE
#         self.C = [0] * 7 # C0は使わないため7個用意
#         for i in range(1, 7):
#             cmd = 0xA0 + (i * 2)
#             data = self.bus.read_i2c_block_data(self.address, cmd, 2)
#             self.C[i] = (data[0] << 8) + data[1]
        
#         # 係数が正しく読めているかデバッグ用
#         # print(f"Calibration Coefficients: {self.C}")

#     def read_adc(self, cmd):
#         # ADC変換開始
#         self.bus.write_byte(self.address, cmd)
#         # 変換待ち (OSR=4096の場合、最大9.04ms必要)
#         time.sleep(0.01)
#         # データ読み出し (24bit)
#         data = self.bus.read_i2c_block_data(self.address, 0x00, 3)
#         return (data[0] << 16) + (data[1] << 8) + data[2]

#     def read_data(self):
#         # --- 温度と気圧の生データを取得 ---
        
#         # D1: デジタル気圧値 (OSR=4096)
#         D1 = self.read_adc(0x48)
        
#         # D2: デジタル温度値 (OSR=4096)
#         D2 = self.read_adc(0x58)

#         # --- データシートに基づいた補正計算 ---
        
#         # 1. 温度計算
#         dT = D2 - (self.C[5] * 256)
#         TEMP = 2000 + (dT * self.C[6] / 8388608)

#         # 2. 温度オフセット計算
#         OFF = (self.C[2] * 131072) + ((self.C[4] * dT) / 64)
#         SENS = (self.C[1] * 65536) + ((self.C[3] * dT) / 128)

#         # 3. 低温時の二次補正 (20℃未満の場合)
#         if TEMP < 2000:
#             T2 = (dT * dT) / 2147483648
#             OFF2 = 5 * ((TEMP - 2000) ** 2) / 2
#             SENS2 = 5 * ((TEMP - 2000) ** 2) / 4
            
#             # さらに-15℃未満の場合の補正
#             if TEMP < -1500:
#                 OFF2 = OFF2 + 7 * ((TEMP + 1500) ** 2)
#                 SENS2 = SENS2 + 11 * ((TEMP + 1500) ** 2) / 2
            
#             TEMP = TEMP - T2
#             OFF = OFF - OFF2
#             SENS = SENS - SENS2

#         # 4. 最終的な気圧計算
#         P = (D1 * SENS / 2097152 - OFF) / 32768
        
#         # 単位変換
#         pressure_hPa = P / 100.0
#         temperature_c = TEMP / 100.0
        
#         return pressure_hPa, temperature_c

#     def get_altitude(self, pressure, sea_level_pressure=1013.25):
#         # 標高計算の公式 (国際標準大気モデル)
#         # h = 44330 * (1 - (P / P0)^(1/5.255))
#         altitude = 44330.0 * (1.0 - math.pow(pressure / sea_level_pressure, 0.1903))
#         return altitude

# # --- メイン処理 ---
# if __name__ == "__main__":
#     # アドレスは i2cdetect で確認したものに合わせて変更 (0x76 または 0x77)
#     sensor = MS5607(address=0x77) 
    
    
#     print("MS5607 Altimeter Reading...")
#     print("-" * 30)

#     try:
#         while True:
#             press, temp = sensor.read_data()
            
#             # 海面気圧(1013.25hPa)を基準とした高度
#             alt = sensor.get_altitude(press)
            
#             print(f"気圧: {press:.2f} hPa | 温度: {temp:.2f} °C | 推定高度: {alt:.2f} m")
#             time.sleep(1)
            
#     except KeyboardInterrupt:
#         print("\n停止しました")