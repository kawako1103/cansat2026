
import time
import random

def make_LatLon():
    vec_LatLon = []
    for _ in range(20):
        # Generate random latitude and longitude (64-bit)
        latitude = random.uniform(-90, 90)
        longitude = random.uniform(-180, 180)
        vec_LatLon.append((latitude, longitude))
        print(latitude, longitude)
        time.sleep(0.05)  # Approx. 20 times per second
    return vec_LatLon

def send_LatLon(vec_LatLon):
    if not vec_LatLon:
        print("No data to send.")
        return
    last_lat, last_lon = vec_LatLon[-1]
    output = f"{last_lat},{last_lon}\r\n"
    # Convert output to ASCII
    ascii_output = ",".join(str(ord(char)) for char in output)
    
    print("Sending LatLon data:", ascii_output)
    
    return ascii_output

def restore_LatLon(ascii_input):
    # Convert ASCII input back to string
    ascii_list = ascii_input.split(',')
    input_str = "".join(chr(int(code)) for code in ascii_list)
    # Split latitude and longitude
    lat_lon = input_str.strip().split(',')
    latitude = float(lat_lon[0])
    longitude = float(lat_lon[1])
    print("Restored Latitude:", latitude)
    print("Restored Longitude:", longitude)




# Test the functions
vec_LatLon = make_LatLon()
ascii_input = send_LatLon(vec_LatLon)
restore_LatLon(ascii_input)
