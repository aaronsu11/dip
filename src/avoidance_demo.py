# USAGE
# python optical_flow.py
# python optical_flow.py --video front.mp4

import cv2 as cv
import numpy as np
import dronekit
import argparse
import imutils

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

# cap1 = cv.VideoCapture(1)
# cap2 = cv.VideoCapture(2)
feature_params = dict(maxCorners=100,
                      qualityLevel=0.5,
                      minDistance=7,
                      blockSize=7)

lk_params = dict(winSize=(15, 15),
                 maxLevel=2,
                 criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

FRAME_SIZE = 800

ret, old_frame = cap.read()
# ret1, frame1 = cap1.read()
# ret2, frame2 = cap2.read()
# old_frame = np.concatenate((frame1, frame2), axis=1)

old_frame = imutils.resize(old_frame, width=FRAME_SIZE)

old_gray = cv.cvtColor(old_frame, cv.COLOR_BGR2GRAY)
p0 = cv.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
fourcc = cv.VideoWriter_fourcc(*'DIVX')
out = cv.VideoWriter('output.avi', fourcc, 20.0, (640, 480))


def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step / 2:h:step, step /
                    2:w:step].reshape(2, -1).astype(int)

    fx, fy = flow[y, x].T

    lines = np.vstack([x, y, x + fx, y + fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    for (x1, y1), (x2, y2) in lines:
        # if ((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)) ** 0.5 > 7:
        if ((x2 - x1) * (x2 - x1) ** 0.5 <= 5) and ((x2 - x1) * (x2 - x1) ** 0.5 > 2) and ((y2 - y1) * (y2 - y1) ** 0.5 <= 5) and ((y2 - y1) * (y2 - y1) ** 0.5 > 2):
            # cv.circle(vis, (x1, y1), 15, (0, 0, 255), -1)
            cv.circle(vis, (x2, y2), 15, (0, 0, 255), -1)

    # cv.polylines(vis, lines, 0, (0, 255, 0))

    return vis


while True:
    ret, frame = cap.read()
    # ret1, frame1 = cap1.read()
    # ret2, frame2 = cap2.read()
    # frame = np.concatenate((frame1, frame2), axis=1)
    if frame is None:
        break

    frame = imutils.resize(frame, width=FRAME_SIZE)

    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # p1, st, err = cv.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    # good_new = p1[st == 1]
    # good_old = p0[st == 1]

    flow = cv.calcOpticalFlowFarneback(
        old_gray, frame_gray, None, 0.5, 5, 15, 3, 5, 1.2, 0)

    a = flow.shape
    # for i, (new, old) in enumerate(zip(good_,new, good_old)):
    #     #     a, b = new.ravel()
    #     #     c, d = old.ravel()
    #     #     cv.circle(frame_gray, (0, 0), 10, [255, 0, 0], -1)
    #     #     if (abs(a-c)*abs(c-d)) > 1000:
    #     #         cv.rectangle(frame_gray, (a, b), (c, d), [0, 255, 0], 3)
    #     #     cv.circle(frame_gray, (a, b) 5, [255, 0, 0], -1)
    # change the quality Level to remove noise
    # cv.imshow("OpticalFlow", frame_gray)
    new_frame = draw_flow(frame_gray, flow)
    frame_HSV = cv.cvtColor(new_frame, cv.COLOR_BGR2HSV)
    frame_threshold = cv.inRange(frame_HSV, (0, 58, 140), (57, 255, 255))
    ret, thresh = cv.threshold(frame_threshold, 50, 255, cv.THRESH_BINARY)
    _, contours, hierarchy = cv.findContours(
        thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for i in range(len(contours)):
        area = cv.contourArea(contours[i])
        if area > FRAME_SIZE**2 / 15 and area < FRAME_SIZE**2 / 5:
            # contours[0] = contours[i]
            x, y, w, h = cv.boundingRect(contours[i])
            cv.rectangle(new_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            center_x = x + w / 2
            center_y = y + h / 2
            # Replace print statements below with mavlink commands
            if (center_x < FRAME_SIZE/5):
                if (x + w <= FRAME_SIZE/5):
                    print("go straight")
                else:
                    print("turn right")
            elif (center_x > FRAME_SIZE/5) and (center_x <= FRAME_SIZE/3):
                print("turn right")
            elif (center_x > FRAME_SIZE*2/3) and (center_x < FRAME_SIZE*4/5):
                print("turn left")
            elif (center_x >= FRAME_SIZE*4/5):
                if (x < FRAME_SIZE*4/5):
                    print("turn left")
                else:
                    print("go straight")
    # save = cv.cvtColor(new_frame, cv.COLOR_GRAY2BGR)
    save = cv.resize(new_frame, (640, 480), fx=0, fy=0,
                     interpolation=cv.INTER_CUBIC)
    out.write(save)
    cv.imshow("OpticalFlow", new_frame)
    cv.imshow("Original", frame_gray)
    old_gray = frame_gray.copy()
    # p0 = good_new.reshape(-1, 1, 2)

    key = cv.waitKey(30)
    if key == ord('q'):
        out.release()
        break
