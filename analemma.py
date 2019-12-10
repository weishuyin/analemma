from sunposition import sunpos
from datetime import datetime,timedelta
import pytz
import urllib2
import json
import argparse
import math
import numpy as np
import matplotlib.pyplot as plt

def getIPAddress():
    response = urllib2.urlopen("http://httpbin.org/ip")
    content = response.read()
    jsonContent = json.loads(content)
    IP = jsonContent["origin"].split(",")[0]
    return IP

def getLatitudeLongitude():
    IP = getIPAddress()
    response = urllib2.urlopen("http://ipinfo.io/" + IP)
    content = response.read()
    jsonContent = json.loads(content)
    latitude,longitude = jsonContent["loc"].split(",")
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
def worldAzimuthZenith2WorldPoint(azimuth, zenith):
    sunDistance = 1.496*math.pow(10, 14) # in mm
    xWorld = sunDistance*math.sin(zenith/180.0*math.pi)*math.sin(azimuth/180.0*math.pi)
    yWorld = sunDistance*math.sin(zenith/180.0*math.pi)*math.cos(azimuth/180.0*math.pi)
    zWorld = sunDistance*math.cos(zenith/180.0*math.pi)
    return np.array([[xWorld],[yWorld],[zWorld]])

def worldPoint2ViewPoint(point, azimuth, pitch, roll):
    Rx = np.array([[1,0,0], [0, math.cos(pitch/180.0*math.pi), -math.sin(pitch/180.0*math.pi)], [0, math.sin(pitch/180.0*math.pi), math.cos(pitch/180.0*math.pi)]])
    Ry = np.array([[math.cos(roll/180.0*math.pi),0,math.sin(roll/180.0*math.pi)], [0,1,0], [-math.sin(roll/180.0*math.pi),0,math.cos(roll/180.0*math.pi)]])
    Rz = np.array([[math.cos(azimuth/180.0*math.pi), -math.sin(azimuth/180.0*math.pi), 0], [math.sin(azimuth/180.0*math.pi), math.cos(azimuth/180.0*math.pi), 0], [0,0,1]])
    matrix = np.dot(Rx, np.dot(Ry, Rz))
    return np.dot(matrix, point)

def viewPoint2ViewAzimuthZenith(point):
    x = point[0,0]
    y = point[1,0]
    z = point[2,0]
    distance = math.sqrt(x*x + y*y + z*z)
    zenith = math.acos(z/distance)/math.pi*180.0
    azimuth = math.atan2(x, y)/math.pi*180.0
    if azimuth < 0:
        azimuth += 360
    return azimuth, zenith

def viewAzimuthZenith2Projection(azimuth, zenith, args):
    if args.facing_back == True and (azimuth >= 90 and azimuth <= 270):
        return None
    if args.facing_back == False and (azimuth <= 90 and azimuth >= -90):
        return None
    x = args.focus_length*math.tan(azimuth/180.0*math.pi)
    y = args.focus_length*math.tan((90-zenith)/180.0*math.pi)
    if x > args.sensor_width/2 or x < -args.sensor_width/2:
        return None
    if y > args.sensor_height/2 or y < -args.sensor_height/2:
        return None
    return x,y

# end of Coordinate System Transforms

def getPoints(args):
    azimuth_list,zenith_list = getSolarPositions(args)
    xs = []
    ys = []
    colors = []
    for i in range(len(azimuth_list)):
        worldPoint = worldAzimuthZenith2WorldPoint(azimuth_list[i], zenith_list[i])
        viewPoint = worldPoint2ViewPoint(worldPoint, args.camera_azimuth, args.camera_pitch, args.camera_roll)
        viewAzimuth, viewZenith = viewPoint2ViewAzimuthZenith(viewPoint)
        ret = viewAzimuthZenith2Projection(viewAzimuth, viewZenith, args)
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
    return xs,ys,colors

def plot(args, xs, ys, colors):
    fig, ax = plt.subplots()
    sun_diameter_in_mm = 1.392/149.6*args.focus_length
    sun_diameter_in_dots = sun_diameter_in_mm/args.sensor_width*fig.get_size_inches()[0]*fig.get_dpi()

    ax.scatter(xs, ys, sun_diameter_in_dots*sun_diameter_in_dots, colors)
    ax.set_xbound(-args.sensor_width/2, args.sensor_width/2)
    ax.set_ybound(-args.sensor_height/2, args.sensor_height/2)
    ax.set_xlabel('x/mm')
    ax.set_ylabel('y/mm')
    if args.save:
        plt.savefig(args.save)
    else:
        plt.show()

def main():
    default_latitude, default_longitude = getLatitudeLongitude()
    parser = argparse.ArgumentParser()
    parser.description = "draw analemma, the Sun runs from red point to green point to blue point"
    parser.add_argument("--camera_azimuth", default=-1000, help="azimuth", type=float)
    parser.add_argument("--camera_pitch", default=-1000, help="pitch", type=float)
    parser.add_argument("--camera_roll", default=0, help="roll", type=float)
    parser.add_argument("--facing_back", default=True, help="camera facing back or not", type=bool)
    parser.add_argument("--focus_length", default=24, help="camera focus length in mm", type=float)
    parser.add_argument("--sensor_width", default=36, help="camera sensor width in mm", type=float)
    parser.add_argument("--sensor_height", default=24, help="camera sensor height in mm", type=float)

    parser.add_argument("--datetime", default=datetime.utcnow(), help="UTC datetime in format %%Y-%%m-%%d H:M:S", type=lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S'))
    parser.add_argument("--npoints_before", default=15, help="number of points before datetime", type=int)
    parser.add_argument("--npoints_after", default=15, help="number of points after datetime", type=int)

    parser.add_argument("--latitude", default=default_latitude, help="latitude", type=float)
    parser.add_argument("--longitude", default=default_longitude, help="longitude", type=float)
    parser.add_argument("--elevation", default=0, help="elevation", type=float)

    parser.add_argument("--save", metavar="FILENAME", nargs="?", const="analemma.png", help="save image", type=str)

    args = parser.parse_args()
    if args.camera_azimuth == -1000 or args.camera_pitch == -1000:
        azimuth_list,zenith_list = getSolarPositions(args)
        default_azimuth = sum(azimuth_list)/len(azimuth_list)
        default_zenith = sum(zenith_list)/len(zenith_list)
        if args.camera_azimuth == -1000:
            args.camera_azimuth = default_azimuth
            print "default camera_azimuth is %f" % args.camera_azimuth
        if args.camera_pitch == -1000:
            args.camera_pitch = default_zenith - 90
            print "default camera_pitch is %f" % args.camera_pitch
    xs, ys, colors = getPoints(args)
    plot(args, xs, ys, colors)

if __name__ == "__main__":
    main()
