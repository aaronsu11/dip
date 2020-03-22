from dronekit import connect, VehicleMode, LocationGlobalRelative, APIException
import time
import socket
import exceptions
import math
import argparse
import sys


def connectVehicle():

    parser = argparse.ArgumentParser(description="commands")
    parser.add_argument("--connect")
    args = parser.parse_args()
    connection_string = args.connect

    if not connection_string:
        print("No connection string provided. Start simulator (SITL)")
        import dronekit_sitl
        try:
            sitl = dronekit_sitl.start_default()
            connection_string = sitl.connection_string()
        except OSError as e:
            print(e)
            print("SITL is only supported for x86 system")
            print(
                "Please provide a physical address to connect to. e.g. --connect 127.0.0.1")
            sys.exit()

    # Connect to the Vehicle.
    print("Connecting to vehicle on: %s" % (connection_string,))
    vehicle = connect(connection_string, wait_ready=True)

    return vehicle


if __name__ == "__main__":
    vehicle = connectVehicle()
