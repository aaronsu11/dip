import cv2
import numpy as np
import argparse
import imutils

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
                help="path to input video file")
args = vars(ap.parse_args())

if not args.get("video", False):
    print("[INFO] starting video stream...")
    cap = cv2.VideoCapture(0)

# otherwise, grab a reference to the video file
else:
    print(args["video"])
    cap = cv2.VideoCapture(args["video"])

ret, frame1 = cap.read()
frame1 = imutils.resize(frame1, width=500)
prvs = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
hsv = np.zeros_like(frame1)
hsv[..., 1] = 255

while(1):
    ret, frame2 = cap.read()
    if frame2 is None:
        break
    frame2 = imutils.resize(frame2, width=500)
    next = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    flow = cv2.calcOpticalFlowFarneback(
        prvs, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    hsv[..., 0] = ang*180/np.pi/2
    hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    cv2.imshow('frame1', frame2)
    cv2.imshow('frame2', rgb)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
    elif k == ord('s'):
        cv2.imwrite('opticalfb.png', frame2)
        cv2.imwrite('opticalhsv.png', rgb)
    prvs = next

cap.release()
cv2.destroyAllWindows()
