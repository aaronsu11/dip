from connection import connectVehicle
from set_states import setVehicleMode, armVehicle
import time


def takeoff(vehicle, altitude, wait=True):
    """Takeoff the vehicle to the target altitude 

    Parameters:
        vehicle: the vehicle object, connected to mavproxy
        altitude: the target altitude to takeoff in meters
        wait (boolean): whether the function should wait (blocking) 
            until the altitude is reached

    Return:
        None

    """

    vehicle.simple_takeoff(altitude)

    while wait:
        print("Current Altitude: %d" %
              vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= 0.95*altitude:
            break
        time.sleep(1)
    print("Target altitude reached")


if __name__ == "__main__":
    vehicle = connectVehicle()
    setVehicleMode(vehicle, "GUIDED")

    print("CAUTION! Props may start spinning!")
    armVehicle(vehicle)
    takeoff(vehicle, 5)

    key = ""
    while (key != "q"):
        key = input()

    vehicle.close()
