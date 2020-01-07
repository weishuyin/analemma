#!/usr/bin/python

# Calculate DLSR's orientation based on position of Sun in photo and corresponding datetime.  
# REF: https://www.geometrictools.com/Documentation/EulerAngles.pdf

from sunposition import sunpos
from datetime import datetime
import numpy as np
import sys
import json
import argparse
import math

# Coordinate System Transforms
def worldAzimuthZenith2WorldPoint(sunAzimuth, sunZenith):
    if sunAzimuth < 0 or sunAzimuth > 360 or sunZenith < 0 or sunZenith > 180:
        print "worldAzimuthZenith2WorldPoint wrong argument %s %s" % (sunAzimuth, sunZenith)
        sys.exit(-1)
    sunDistanceInMM = 1.496*math.pow(10, 14) # in mm
    xWorld = sunDistanceInMM*math.sin(sunZenith/180.0*math.pi)*math.sin(sunAzimuth/180.0*math.pi)
    yWorld = sunDistanceInMM*math.sin(sunZenith/180.0*math.pi)*math.cos(sunAzimuth/180.0*math.pi)
    zWorld = sunDistanceInMM*math.cos(sunZenith/180.0*math.pi)
    worldPoint = np.array([[xWorld],[yWorld],[zWorld]])
    return worldPoint

def projection2ViewPoint(xInMM, yInMM, focal_length, sensor_width, sensor_height, facing_back):
    sunDistanceInMM = 1.496*math.pow(10, 14) # in mm
    if facing_back == True:
        z = -abs(math.sqrt(sunDistanceInMM*sunDistanceInMM/(1.0*xInMM*xInMM/focal_length/focal_length + 1.0*yInMM*yInMM/focal_length/focal_length + 1)))
        x = -xInMM*z/focal_length
        y = -yInMM*z/focal_length
    else:
        z = abs(math.sqrt(sunDistanceInMM*sunDistanceInMM/(1.0*xInMM*xInMM/focal_length/focal_length + 1.0*yInMM*yInMM/focal_length/focal_length + 1)))
        x = xInMM*z/focal_length
        y = yInMM*z/focal_length
    viewPoint = np.array([[x],[y],[z]])
    return viewPoint
# end of Coordinate System Transforms

def pixel2MM(xInPixel, yInPixel, pixel_width, pixel_height, sensor_width, sensor_height):
    xInMM = 1.0*xInPixel/pixel_width*sensor_width - sensor_width/2
    yInMM = -(1.0*yInPixel/pixel_height*sensor_height - sensor_height/2)
    return xInMM,yInMM

def getOrientation(worldPoints, viewPoints):
    count = 0
    total = worldPoints.shape[1]/3*3
    cameraAzimuthSum = 0.0
    cameraPitchSum = 0.0
    cameraRollSum = 0.0
    for i in range(total):
        worldPointArray = worldPoints[:,:(i+1)*3]
        viewPointArray = viewPoints[:,:(i+1)*3]
        matrix = np.dot(viewPointArray, np.linalg.inv(worldPointArray))
        if matrix[1,2] < 1.0:
            if matrix[1,2] > -1.0:
                cameraPitch = math.asin(-matrix[1,2])/math.pi*180.0
                cameraRoll = math.atan2(matrix[0,2], matrix[2,2])/math.pi*180.0
                cameraAzimuth = math.atan2(matrix[1,0], matrix[1,1])/math.pi*180.0
            else:
                continue
                # cameraPitch = 90.0
                # cameraRoll = 0.0
                # cameraAzimuth = math.atan2(-matrix[0,1], matrix[0,0])/math.pi*180.0
        else:
            continue
            # cameraPitch = -90.0
            # cameraRoll = 0
            # cameraAzimuth = math.atan2(-matrix[0,1], matrix[0,0])/math.pi*180.0
        cameraAzimuthSum += cameraAzimuth
        cameraPitchSum += cameraPitch
        cameraRollSum += cameraRoll
        count += 1
    if count == 0:
        return None, None, None
    return cameraAzimuthSum/count, cameraPitchSum/count, cameraRollSum/count

def solve(args):
    datalist = json.loads(args.data)
    worldPoints = np.empty(shape=[3, 0])
    viewPoints = np.empty(shape=[3, 0])
    for i in range(len(datalist)):
        data = datalist[i]
        xInPixel = data[0]
        yInPixel = data[1]
        date = datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S')
        azimuth, zenith = sunpos(date, latitude=args.latitude, longitude=args.longitude, elevation=args.elevation)[:2]
        worldPoint = worldAzimuthZenith2WorldPoint(azimuth, zenith)
        xInMM, yInMM = pixel2MM(xInPixel, yInPixel, args.pixel_width, args.pixel_height, args.sensor_width, args.sensor_height)
        viewPoint = projection2ViewPoint(xInMM, yInMM, args.focal_length, args.sensor_width, args.sensor_height, args.facing_back)
        worldPoints = np.append(worldPoints, worldPoint, 1)
        viewPoints = np.append(viewPoints, viewPoint, 1)
    cameraAzimuth, cameraPitch, cameraRoll = getOrientation(worldPoints, viewPoints)
    return cameraAzimuth,cameraPitch, cameraRoll

def main():
    parser = argparse.ArgumentParser()
    parser.description = "solve DSLR's azimuth, pitch and roll"
    parser.add_argument("--latitude", help="latitude", type=float)
    parser.add_argument("--longitude", help="longitude", type=float)
    parser.add_argument("--elevation", default=0, help="elevation", type=float)

    parser.add_argument("--data", help="[[x in pixel, y in pixel, datetime in UTC format %%Y-%%m-%%d %%H:%%M:%%S], ...]", type=str)

    parser.add_argument("--facing_back", default=True, help="camera facing back or not", type=lambda s: s == "True")
    parser.add_argument("--focal_length", default=24, help="camera focal length in mm", type=float)
    parser.add_argument("--sensor_width", default=36, help="camera sensor width in mm", type=float)
    parser.add_argument("--sensor_height", default=24, help="camera sensor height in mm", type=float)
    parser.add_argument("--pixel_width", default=5760, help="image width in pixel", type=int)
    parser.add_argument("--pixel_height", default=3840, help="image height in pixel", type=int)

    args = parser.parse_args()
    if args.data == None:
        parser.print_help()
        sys.exit(-1)

    cameraAzimuth, cameraPitch, cameraRoll = solve(args)
    print "cameraAzimuth=%f cameraPitch=%f cameraRoll=%f" % (cameraAzimuth,cameraPitch, cameraRoll)

if __name__ == "__main__":
    main()
