import cv2 as cv
import numpy as np
import dronekit as dk
from pymavlink import mavutil
import time
import argparse
import imutils
import threading
import enum

from connection import connectVehicle
from actions import arm_and_takeoff, send_ned_velocity, goto_position_target_local_ned
from obstacle import draw_flow, detect_obstacle

FRAME_SIZE = 500
WPX = 28.623038
WPY = 77.260373 - 0.003

class Command(enum.Enum):
    Straight = 0
    Left = 1
    Right = 2

def sendCommand(vehicle, command):
        if command is Command.Left:
            print("Turning Left")
            goto_position_target_local_ned(vehicle, 0, -2, 0)  # move left for 0.5 meters
        elif command is Command.Right:
            print("Turning Right")
            goto_position_target_local_ned(vehicle, 0, 2, 0)  # move left for 0.5 meters
        else:
            vehicle.simple_goto(waypoint)  # continue the journey

if __name__ == "__main__":

    cap = cv.VideoCapture("/home/student/Videos/SIM001.mp4")
    # cap = cv.VideoCapture(0)

    ret, old_frame = cap.read()
    old_frame = imutils.resize(old_frame, width=FRAME_SIZE)
    old_gray = cv.cvtColor(old_frame, cv.COLOR_BGR2GRAY)

    vehicle = connectVehicle()

    fourcc = cv.VideoWriter_fourcc(*'XVID')
    out = cv.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    waypoint = dk.LocationGlobalRelative(WPX,WPY, 10)  # Destination

    arm_and_takeoff(vehicle, 10)
    vehicle.airspeed = 10
    vehicle.simple_goto(waypoint)

    while True:
        # print("continue to the waypoint")
        # vehicle.simple_goto(waypoint)
        ret, frame = cap.read()
        if frame is None:
            break
        frame = imutils.resize(frame, width=FRAME_SIZE)
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        flow = cv.calcOpticalFlowFarneback(
            old_gray, frame_gray, None, 0.5, 5, 30, 3, 5, 1.2, 0)
        # Mark flows on the frame by red dots
        new_frame = draw_flow(frame_gray, flow)

        contours = detect_obstacle(new_frame)

        obstacle_left = False
        obstacle_right = False
        obstacle_center = False

        for i in range(len(contours)):
            area = cv.contourArea(contours[i])
            # Condition to filter unwanted regions or objects
            if area > FRAME_SIZE**2 / 20 and area < FRAME_SIZE**2 / 5:
                # contours[0] = contours[i]
                x, y, w, h = cv.boundingRect(contours[i])
                cv.rectangle(frame_gray, (x, y), (x + w, y + h), (255, 0, 0), 2)
                center_x = x + w / 2
                # center_y = y + h / 2
                if (center_x < FRAME_SIZE/5):
                    if (x + w <= FRAME_SIZE/5):
                        # print("go straight")
                        pass
                    else:
                        obstacle_left = True
                        # print("turn right")
                elif (center_x > FRAME_SIZE/5) and (center_x <= FRAME_SIZE/2):
                    obstacle_left = True
                    # print("turn right")
                elif (center_x > FRAME_SIZE*1/2) and (center_x < FRAME_SIZE*4/5):
                    obstacle_right = True
                    # print("turn left")
                elif (center_x >= FRAME_SIZE*4/5):
                    if (x - w < FRAME_SIZE*4/5):
                        obstacle_right = True
                        # print("turn left")
                    else:
                        # print("go straight")
                        pass

        command = Command.Straight
        if obstacle_left and not obstacle_right:
            command = Command.Right
            # print("turn right")
        elif obstacle_right and not obstacle_left:
            command = Command.Left
            # print("turn left")
        else:
            pass
            # print("go straight")
        t = threading.Thread(target=sendCommand, args=[vehicle, command])
        t.start()

        save = cv.cvtColor(frame_gray, cv.COLOR_GRAY2BGR)
        # temp = cv.resize(save, (640, 480), fx=0, fy=0, interpolation=cv.INTER_CUBIC)
        out.write(save)
        cv.imshow("OpticalFlow", new_frame)
        cv.imshow("Original", frame_gray)
        old_gray = frame_gray.copy()

        key = cv.waitKey(200)
        if key == ord('q'):
            out.release()
            break

        lat = vehicle.location.global_relative_frame.lat  # get the current latitude
        lon = vehicle.location.global_relative_frame.lon  # get the current longitude
        if round(lat, 5) == round(WPX, 5) and round(lon, 5) == round(WPY, 5):  # check whether the vehicle is arrived or not
            print("Arrived")
            out.release()
            break

    print("Landing")
    vehicle.mode = dk.VehicleMode("LAND")
    vehicle.flush()

    vehicle.close()