from dronekit import VehicleMode
import time

from connection import connectVehicle


def setVehicleMode(vehicle, mode="GUIDED"):
    """Set vehicle mode

    Parameters:
        vehicle: the vehicle object, connected to mavproxy
        mode(string): the target vehicle mode. e.g. GUIDED

    Return:
        None

    """

    vehicle.mode = VehicleMode(mode)
    print("Waiting for vehicle to enter %s mode" % mode)
    while vehicle.mode != mode:
        print("."),
        time.sleep(1)
    print("Vehicle is now %s mode!" % mode)


if __name__ == "__main__":
    vehicle = connectVehicle()
    setVehicleMode(vehicle, "GUIDED")
    time.sleep(3)

    vehicle.close()
