from dronekit import connect, VehicleMode, LocationGlobalRelative, APIException
import time
import socket
import exceptions
import math
import argparse


def connectVehicle():

    parser = argparse.ArgumentParser(description="commands")
    parser.add_argument("--connect")
    args = parser.parse_args()
    connection_string = args.connect

    if not connection_string:
        print ("No connection string provided. Start simulator (SITL)")
        import dronekit_sitl
        sitl = dronekit_sitl.start_default()
        connection_string = sitl.connection_string()

    # Connect to the Vehicle.
    print("Connecting to vehicle on: %s" % (connection_string,))
    vehicle = connect(connection_string, wait_ready=True)

    return vehicle


if __name__ == "__main__":
    vehicle = connectVehicle()
