"""
Saves a series of snapshots with the current camera as snapshot_<width>_<height>_<nnn>.jpg

Arguments:
    --f <output folder>     default: current folder
    --n <file name>         default: snapshot
    --w <width px>          default: none
    --h <height px>         default: none
    --cross <True/False>    display + adn x cross hair at centre of the image taken
    --addpose <True/False>  roll pitch and yaw angles are placed in captured filename. Assumption: pixhawk connected to USB of raspberryPi3. Example 
                            filename would be like:  pose_test_640_480_p0.025_r0.003_y-1.864_a6.570_22


Buttons:
    q           - quit
    space bar   - save the snapshot
    
Sample command:
    python ./save_snapshots.py --folder test_rpy --name rpytest --dwidth 640 --dheight 480 --raspi True --cross True --addpose True
    python ./save_snapshots.py --folder at_home2 --name pose_test --dwidth 640 --dheight 480 --raspi True --cross True --addpose True

"""

import cv2
import time
import sys
import argparse
import os

__author__ = "Tiziano Fiorenzani"
__date__ = "01/06/2018"
__credits__="Manish Shrestha"
__contribution_date__="06/10/2018"


def save_snaps(width=0, height=0, name="snapshot", folder=".", raspi=False, show_crosshair=False, add_pose=False):

    if raspi:
        os.system('sudo modprobe bcm2835-v4l2')
        if add_pose==True:
            from dronekit import connect, VehicleMode
            connection_string ="/dev/ttyACM0" #raspberry USB to Pixhawk
            print("Connecting to vehicle on: %s" % (connection_string,))
            try:
                vehicle = connect(connection_string, wait_ready=True)
                print("Connected to vehicle on: %s" % (connection_string,))
            except Exception, e:
                print ("Error while connecting to the vechile: Error=%r", e)



    cap = cv2.VideoCapture(0)
    if width > 0 and height > 0:
        print "Setting the custom Width and Height"
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
            # ----------- CREATE THE FOLDER -----------------
            folder = os.path.dirname(folder)
            try:
                os.stat(folder)
            except:
                os.mkdir(folder)
    except:
        pass

    nSnap   = 0
    w       = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    h       = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    if h < w:
        sdim = h #smallest dimension
    else:
        sdim = w

    fileName    = "%s/%s_%d_%d_" %(folder, name, w, h)
    while True:
        ret, frame = cap.read()

        if add_pose and raspi:
            att = vehicle.attitude
            alt = vehicle.location.global_relative_frame.alt

        #draw cross at center, diagonals
        if show_crosshair == True:
            cv2.line(frame,(int(w*0.45),int(h/2)),(int(w*0.55),int(h/2)),(255,0,0),1)
            cv2.line(frame,(int(w/2),int(h*0.45)),(int(w/2),int(h*0.55)),(255,0,0),1)
            cv2.line(frame,(int(w/2 - sdim/2),int(h/2-sdim/2)),(int(w/2+sdim/2),int(h/2+sdim/2)),(0,255,0),1)
            cv2.line(frame,(int(w/2 - sdim/2),int(h/2+sdim/2)),(int(w/2+sdim/2),int(h/2-sdim/2)),(0,255,0),1)


        cv2.imshow('camera', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord(' '):
            print "Saving image ", nSnap
            cv2.imwrite("%sp%0.3f_r%0.3f_y%0.3f_a%0.3f_%d.jpg"%(fileName, att.pitch, att.roll, att.yaw, alt, nSnap), frame)
            nSnap += 1

    cap.release()
    cv2.destroyAllWindows()




def main():
    # ---- DEFAULT VALUES ---
    SAVE_FOLDER = "."
    FILE_NAME = "snapshot"
    FRAME_WIDTH = 0
    FRAME_HEIGHT = 0

    # ----------- PARSE THE INPUTS -----------------
    parser = argparse.ArgumentParser(
        description="Saves snapshot from the camera. \n q to quit \n spacebar to save the snapshot")
    parser.add_argument("--folder", default=SAVE_FOLDER, help="Path to the save folder (default: current)")
    parser.add_argument("--name", default=FILE_NAME, help="Picture file name (default: snapshot)")
    parser.add_argument("--dwidth", default=FRAME_WIDTH, type=int, help="<width> px (default the camera output)")
    parser.add_argument("--dheight", default=FRAME_HEIGHT, type=int, help="<height> px (default the camera output)")
    parser.add_argument("--raspi", default=False, type=bool, help="<bool> True if using a raspberry Pi")
    parser.add_argument("--cross", default=False, type=bool, help="<bool> True if cross hair is to be displayed at center")
    parser.add_argument("--addpose", default=False, type=bool, help="<bool> True if roll pitch and yaw angles are to be captured")
    args = parser.parse_args()

    SAVE_FOLDER = args.folder
    FILE_NAME = args.name
    FRAME_WIDTH = args.dwidth
    FRAME_HEIGHT = args.dheight


    save_snaps(width=args.dwidth, height=args.dheight, name=args.name, folder=args.folder, raspi=args.raspi, show_crosshair=args.cross, add_pose=args.addpose)

    print "Files saved"

if __name__ == "__main__":
    main()



