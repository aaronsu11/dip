import time
from connection import connectVehicle

if __name__ == "__main__":
    vehicle = connectVehicle()
    
    while True:
        nextwaypoint=vehicle.commands.next

        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)

        print 'Distance to waypoint (%s): %s' % (nextwaypoint, current_time)

        time.sleep(1)