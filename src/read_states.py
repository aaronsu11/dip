from connection import connectVehicle


def readVehicleStates(vehicle):

    vehicle.wait_ready("autopilot_version")

    #Version and attributes
    print("Autopilot version: %s" % vehicle.version)
    # Firmware support for companion computer
    print("Supports set attitude from companion: %s" %
          vehicle.capabilities.set_attitude_target_local_ned)
    # Read actual position
    print("Position: %s" % vehicle.location.global_relative_frame)
    # Read actual attitude: roll, pitch, yaw
    print("Attitude: %s" % vehicle.attitude)
    # Read actual velocity
    print("Velocity: %s" % vehicle.velocity)  # North, East, Down
    # Last heartbeat
    print("Last Heartbeat: %s" % vehicle.last_heartbeat)
    # Good to arm?
    print("Vehicle armable: %" % vehicle.is_armable)
    # Ground speed
    print("Ground Speed: %s" % vehicle.groundspeed)  # settable
    # Flight mode
    print("Flight Mode: %s" % vehicle.mode.name)  # settable
    # Vehicle Armed?
    print("Vehicle Armed: %s" % vehicle.armed)  # settable
    # Extended Kalman Filter ready?
    print("EKF OK: %s" % vehicle.ekf_ok)


if __name__ == "__main__":
    vehicle = connectVehicle()
    readVehicleStates(vehicle)
    vehicle.close()
