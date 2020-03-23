from dronekit import VehicleMode
from connection import connectVehicle
import time


def setVehicleMode(vehicle, mode):
    """Set vehicle mode

    Parameters:
        vehicle: the vehicle object, connected to mavproxy
        mode(string): the target vehicle mode. e.g. GUIDED

    Return:
        None

    """

    vehicle.mode = VehicleMode(mode)
    print("Waiting for vehicle to enter %s mode" % mode, end="")
    while vehicle.mode != mode:
        print(".", end="")
        time.sleep(1)
    print("Vehicle is now %s mode!" % mode)


def armVehicle(vehicle):
    """Arm the vehicle
    !!!CAUTION (for drone)!!! Propeller will start spinning!

    Parameters:
        vehicle: the vehicle object, connected to mavproxy

    Return:
        None

    """

    print("Waiting for vehicle to become armable", end=""),
    while vehicle.is_armable != True:
        print(".", end="")
        time.sleep(1)
    print("Vehicle is ready to arm!")

    vehicle.armed = True
    print("Waiting for vehicle to arm", end="")
    while vehicle.armed != True:
        print(".", end="")
        time.sleep(1)
    print("Vehicle is now armed!")


if __name__ == "__main__":
    vehicle = connectVehicle()
    setVehicleMode(vehicle, "GUIDED")

    print("CAUTION! Props may start spinning!")
    armVehicle(vehicle)
    time.sleep(3)

    vehicle.close()
