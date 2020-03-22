from connection import connectVehicle


def readVehicleStates(vehicle):

    vehicle.wait_ready("autopilot_version")

    #Version and attributes
    print(f"Autopilot version: {vehicle.version}")


if __name__ == "__main__":
    vehicle = connectVehicle()
    readVehicleStates(vehicle)
