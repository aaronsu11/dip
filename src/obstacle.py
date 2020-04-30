# USAGE
# python optical_flow.py
# python optical_flow.py --video front.mp4
import cv2 as cv
import numpy as np
import dronekit
import argparse
import imutils
import time
import threading
import enum


class Command(enum.Enum):
    Straight = 0
    Left = 1
    Right = 2


def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step / 2:h:step, step /
                    2:w:step].reshape(2, -1).astype(int)

    fx, fy = flow[y, x].T

    lines = np.vstack([x, y, x + fx, y + fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    for (x1, y1), (x2, y2) in lines:
        if ((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)) ** 0.5 > 7:
            cv.circle(vis, (x2, y2), 15, (0, 0, 255), -1)

    return vis


def detect_obstacle(frame):
    frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    frame_threshold = cv.inRange(frame_HSV, (0, 58, 140), (57, 255, 255))
    _, thresh = cv.threshold(frame_threshold, 50, 255, cv.THRESH_BINARY)
    _, contours, _ = cv.findContours(
        thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    return contours


def do_something(command):
    if command:
        if command is Command.Left:
            print("Turning Left")
        elif command is Command.Right:
            print("Turning Right")
        time.sleep(1)


if __name__ == "__main__":
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", type=str,
                    help="path to input video file")
    args = vars(ap.parse_args())

    if not args.get("video", False):
        print("[INFO] starting video stream...")
        cap = cv.VideoCapture(0)

    # otherwise, grab a reference to the video file
    else:
        print(args["video"])
        cap = cv.VideoCapture(args["video"])

    FRAME_SIZE = 500

    ret, old_frame = cap.read()

    old_frame = imutils.resize(old_frame, width=FRAME_SIZE)

    old_gray = cv.cvtColor(old_frame, cv.COLOR_BGR2GRAY)

    fourcc = cv.VideoWriter_fourcc(*'DIVX')
    out = cv.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    while True:

        start = time.perf_counter()

        ret, frame = cap.read()

        if frame is None:
            break

        frame = imutils.resize(frame, width=FRAME_SIZE)

        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        flow = cv.calcOpticalFlowFarneback(
            old_gray, frame_gray, None, 0.5, 5, 15, 3, 5, 1.2, 0)

        new_frame = draw_flow(frame_gray, flow)

        contours = detect_obstacle(new_frame)

        obstacle_left = False
        obstacle_right = False
        obstacle_center = False

        for i in range(len(contours)):
            area = cv.contourArea(contours[i])
            if area > FRAME_SIZE**2 / 20 and area < FRAME_SIZE**2 / 5:
                # contours[0] = contours[i]
                x, y, w, h = cv.boundingRect(contours[i])
                cv.rectangle(new_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                center_x = x + w / 2
                center_y = y + h / 2
                # Replace print statements below with mavlink commands
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

        t = threading.Thread(target=do_something, args=[command])
        t.start()

        save = cv.resize(new_frame, (640, 480), fx=0, fy=0,
                         interpolation=cv.INTER_CUBIC)
        out.write(save)
        cv.imshow("OpticalFlow", new_frame)
        cv.imshow("Original", frame_gray)
        old_gray = frame_gray.copy()

        finish = time.perf_counter()

        key = cv.waitKey(1)
        if key == ord('q'):
            out.release()
            break

        print("%ssec" % round(finish-start, 4))
