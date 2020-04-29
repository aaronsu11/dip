import argparse

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
                help="path to input video file")
args = vars(ap.parse_args())

if not args.get("video", False):
    print("HI")
else:
    print(args)
