#!/usr/bin/python

# Simulate analemma photo based on GPS info, DSLR's orientation, DSLR's CMOS info

from sunposition import sunpos
from datetime import datetime,timedelta
import urllib2
import json
import argparse
import sys
import math
import numpy as np
import matplotlib.pyplot as plt

def getIPAddress():
    response = urllib2.urlopen("http://httpbin.org/ip")
    content = response.read()
    jsonContent = json.loads(content)
    IP = jsonContent["origin"].split(",")[0]
    print "ip=%s" % IP
    return IP

def getLatitudeLongitude():
    print "auto detecting latitude&longitude, may be very slow"
    IP = getIPAddress()
    response = urllib2.urlopen("http://ipinfo.io/" + IP)
    content = response.read()
    jsonContent = json.loads(content)
    latitude,longitude = jsonContent["loc"].split(",")
    latitude = float(latitude)
    longitude = float(longitude)
    print "latitude=%f longitude=%f" % (latitude, longitude)
    return latitude,longitude

def getDateTimes(date, npoints_before, npoints_after):
    delta = 365/(npoints_before + npoints_after)
    result = []
    for i in range(-npoints_before, npoints_after+1):
        result.append(date + timedelta(days = delta*i))
    return result

def getSolarPositions(args):
    dates = getDateTimes(args.datetime, args.npoints_before, args.npoints_after)
    azimuth_list = []
    zenith_list = []
    for date in dates:
        azimuth,zenith = sunpos(date, latitude=args.latitude, longitude=args.longitude, elevation=args.elevation)[:2]
        azimuth_list.append(azimuth)
        zenith_list.append(zenith)
    return azimuth_list,zenith_list

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

def worldPoint2ViewPoint(worldPoint, cameraAzimuth, cameraPitch, cameraRoll):
    Rx = np.array([[1,0,0], [0, math.cos(cameraPitch/180.0*math.pi), -math.sin(cameraPitch/180.0*math.pi)], [0, math.sin(cameraPitch/180.0*math.pi), math.cos(cameraPitch/180.0*math.pi)]])
    Ry = np.array([[math.cos(cameraRoll/180.0*math.pi),0,math.sin(cameraRoll/180.0*math.pi)], [0,1,0], [-math.sin(cameraRoll/180.0*math.pi),0,math.cos(cameraRoll/180.0*math.pi)]])
    Rz = np.array([[math.cos(cameraAzimuth/180.0*math.pi), -math.sin(cameraAzimuth/180.0*math.pi), 0], [math.sin(cameraAzimuth/180.0*math.pi), math.cos(cameraAzimuth/180.0*math.pi), 0], [0,0,1]])
    matrix = np.dot(Ry, np.dot(Rx, Rz))
    viewPoint = np.dot(matrix, worldPoint)
    return viewPoint

def viewPoint2Projection(viewPoint, focal_length, sensor_width, sensor_height, facing_back):
    x = viewPoint[0,0]
    y = viewPoint[1,0]
    z = viewPoint[2,0]
    if facing_back == True:
        if z >= 0.0:
            return None
        xInMM = focal_length*x/(-z)
        yInMM = focal_length*y/(-z)
    else:
        if z <= 0.0:
            return None
        xInMM = focal_length*x/z
        yInMM = focal_length*y/z
    if xInMM > sensor_width/2 or xInMM < -sensor_width/2:
        return None
    if yInMM > sensor_height/2 or yInMM < -sensor_height/2:
        return None
    return xInMM,yInMM

# end of Coordinate System Transforms

def mm2Pixel(args, point):
    xInPixel = (point[0] + args.sensor_width/2.0)/args.sensor_width*args.pixel_width
    yInPixel = (-point[1] + args.sensor_height/2.0)/args.sensor_height*args.pixel_height
    return int(xInPixel),int(yInPixel)

def getPoints(args):
    azimuth_list,zenith_list = getSolarPositions(args)
    xs = []
    ys = []
    colors = []
    for i in range(len(azimuth_list)):
        worldPoint = worldAzimuthZenith2WorldPoint(azimuth_list[i], zenith_list[i])
        viewPoint = worldPoint2ViewPoint(worldPoint, args.camera_azimuth, args.camera_pitch, args.camera_roll)
        ret = viewPoint2Projection(viewPoint, args.focal_length, args.sensor_width, args.sensor_height, args.facing_back)
        if not ret:
            continue;
        if i == args.npoints_before - 1:
            colors.append("#ff0000")
        elif i == args.npoints_before:
            colors.append("#00ff00")
        elif i == args.npoints_before + 1:
            colors.append("#0000ff")
        else:
            colors.append("#ffff00")
        xs.append(ret[0])
        ys.append(ret[1])
        xInPixel,yInPixel = mm2Pixel(args, ret)
        print "In image (x,y) = (%d,%d)" % (xInPixel,yInPixel)
    return xs,ys,colors

def plot(args, xs, ys, colors):
    fig, ax = plt.subplots()
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    sun_diameter_in_mm = 1.392/149.6*args.focal_length
    sun_diameter_in_dots = sun_diameter_in_mm/args.sensor_width*bbox.width*fig.get_dpi()

    ax.scatter(xs, ys, sun_diameter_in_dots*sun_diameter_in_dots, colors)
    ax.set_xbound(-args.sensor_width/2, args.sensor_width/2)
    ax.set_ybound(-args.sensor_height/2, args.sensor_height/2)
    ax.set_xlabel('x/mm')
    ax.set_ylabel('y/mm')
    ax.set_aspect('equal');
    if args.save:
        plt.savefig(args.save)
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.description = "draw analemma, the Sun runs from red point to green point to blue point"
    parser.add_argument("--camera_azimuth", default=-1000, help="azimuth", type=float)
    parser.add_argument("--camera_pitch", default=-1000, help="pitch", type=float)
    parser.add_argument("--camera_roll", default=-1000, help="roll", type=float)
    parser.add_argument("--facing_back", default=True, help="camera facing back or not", type=lambda s: s == "True")
    parser.add_argument("--focal_length", default=24, help="camera focal length in mm", type=float)
    parser.add_argument("--sensor_width", default=36, help="camera sensor width in mm", type=float)
    parser.add_argument("--sensor_height", default=24, help="camera sensor height in mm", type=float)
    parser.add_argument("--pixel_width", default=5760, help="image width in pixel", type=int)
    parser.add_argument("--pixel_height", default=3840, help="image height in pixel", type=int)

    parser.add_argument("--datetime", default=datetime.utcnow(), help="UTC datetime in format %%Y-%%m-%%d H:M:S", type=lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S'))
    parser.add_argument("--npoints_before", default=15, help="number of points before datetime", type=int)
    parser.add_argument("--npoints_after", default=15, help="number of points after datetime", type=int)

    parser.add_argument("--latitude", help="latitude", type=float)
    parser.add_argument("--longitude", help="longitude", type=float)
    parser.add_argument("--elevation", default=0, help="elevation", type=float)

    parser.add_argument("--save", metavar="FILENAME", nargs="?", const="analemma.png", help="save image", type=str)

    args = parser.parse_args()
    if args.latitude == None or args.longitude == None:
        args.latitude, args.longitude = getLatitudeLongitude()
    if args.camera_azimuth == -1000 or args.camera_pitch == -1000 or args.camera_roll == -1000:
        marchDateTime = args.datetime - timedelta(days = (args.datetime.month - 3)*30)
        default_azimuth, default_zenith = sunpos(marchDateTime, latitude=args.latitude, longitude=args.longitude, elevation=args.elevation)[:2]
        # if args.facing_back == True:
        #     args.camera_azimuth = default_azimuth
        #     args.camera_pitch = default_zenith - 180.0
        #     args.camera_roll = 0.0
        # else:
        #     args.camera_azimuth = default_azimuth - 180.0
        #     if args.camera_azimuth < 0.0:
        #         args.camera_azimuth += 360.0
        #     args.camera_pitch = -default_zenith
        #     args.camera_roll = 0.0
        if default_zenith <= 90.0:
            args.camera_azimuth = default_azimuth - 180.0
            if args.camera_azimuth < 0:
                args.camera_azimuth += 360.0
            args.camera_pitch = -default_zenith
            args.camera_roll = 180.0
        else:
            args.camera_azimuth = default_azimuth
            args.camera_pitch = default_zenith - 180.0
            args.camera_roll = 0.0
        if args.facing_back == False:
            args.camera_roll += 180.0
            if args.camera_roll > 180.0:
                args.camera_roll -= 360.0
        print "default camera_azimuth is %f" % args.camera_azimuth
        print "default camera_pitch is %f" % args.camera_pitch
        print "default camera_roll is %f" % args.camera_roll
    xs, ys, colors = getPoints(args)
    plot(args, xs, ys, colors)

if __name__ == "__main__":
    main()
