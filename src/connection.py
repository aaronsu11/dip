from dronekit import connect, LocationGlobalRelative, APIException
# import socket
# import exceptions
# import math
import argparse
import sys


def connectVehicle():

    parser = argparse.ArgumentParser(description="commands")
    parser.add_argument("--connect")
    args = parser.parse_args()
    connection_string = args.connect
    baud_rate = 115200

    if not connection_string:
        try:
            print("No connection string provided. Start simulator (SITL)")
            import dronekit_sitl
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
    vehicle = connect(connection_string, baud=baud_rate, wait_ready=True)

    return vehicle


if __name__ == "__main__":
    vehicle = connectVehicle()
    vehicle.close()
