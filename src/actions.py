import dronekit as dk
from pymavlink import mavutil
import time

from connection import connectVehicle
from set_states import setVehicleMode

def armVehicle(vehicle):
    """Arm the vehicle
    !!!CAUTION (for drone)!!! Propeller will start spinning!

    Parameters:
        vehicle: the vehicle object, connected to mavproxy

    Return:
        None

    """

    print("Waiting for vehicle to become armable")
    while vehicle.is_armable != True:
        print("."),
        time.sleep(1)
    print("Vehicle is ready to arm!")

    vehicle.armed = True
    print("Waiting for vehicle to arm")
    while vehicle.armed != True:
        print("."),
        time.sleep(1)
    print("Vehicle is now armed!")

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

def arm_and_takeoff(vehicle, aTargetAltitude):
    print("Basic pre-arm checks")
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    vehicle.mode = dk.VehicleMode("GUIDED")
    vehicle.armed = True
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


def send_ned_velocity(vehicle, velocity_x, velocity_y, velocity_z):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,  # time_boot_ms (not used)
        0, 0,  # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_NED,  # frame
        0b0000111111000111,  # type_mask (only speeds enabled)
        0, 0, 0,  # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z,  # x, y, z velocity in m/s
        # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0, 0,
        0, 0)  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
    vehicle.send_mavlink(msg)
    vehicle.flush()


def goto_position_target_local_ned(vehicle, north, east, down):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,  # time_boot_ms (not used)
        0, 0,  # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_NED,  # frame
        0b0000111111111000,  # type_mask (only positions enabled)
        # x, y, z positions (or North, East, Down in the MAV_FRAME_BODY_NED frame
        north, east, down,
        0, 0, 0,  # x, y, z velocity in m/s  (not used)
        # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0, 0,
        0, 0)  # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
    # send command to vehicle
    vehicle.send_mavlink(msg)
    vehicle.flush()


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
