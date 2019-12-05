from sunposition import sunpos
from datetime import datetime,timedelta
import pytz
import urllib2
import json
import argparse
import math
import matplotlib.pyplot as plt

def getIP():
    response = urllib2.urlopen("http://httpbin.org/ip")
    content = response.read()
    jsonContent = json.loads(content)
    IP = jsonContent["origin"].split(",")[0]
    return IP

def getLatLon():
    IP = getIP()
    response = urllib2.urlopen("http://ipinfo.io/" + IP)
    content = response.read()
    jsonContent = json.loads(content)
    latitude,longitude = jsonContent["loc"].split(",")
    return latitude,longitude

def getDates(date, npoints_before, npoints_after):
    delta = 365/(npoints_before + npoints_after)
    result = []
    for i in range(npoints_before+1):
        result.insert(0, date - timedelta(days = delta*i))
    for i in range(1, npoints_after+1):
        result.append(date + timedelta(days = delta*i))
    return result

def getAzimuthZenithList(args):
    dates = getDates(args.datetime, args.npoints_before, args.npoints_after)
    azimuth_list = []
    zenith_list = []
    for date in dates:
        azimuth,zenith = sunpos(date, latitude=args.latitude, longitude=args.longitude, elevation=args.elevation)[:2]
        azimuth_list.append(azimuth)
        zenith_list.append(zenith)
    return azimuth_list,zenith_list

def getXYs(args):
    azimuth_list,zenith_list = getAzimuthZenithList(args)
    xs = []
    ys = []
    colors = []
    for i in range(len(azimuth_list)):
        if abs(args.camera_azimuth - azimuth_list[i]) >= 180:
            continue
        if args.camera_zenith <= 0 or args.camera_zenith >= 90:
            continue
        xi = args.focus_length * math.tan((azimuth_list[i] - args.camera_azimuth)/180.0*math.pi)
        yi = args.focus_length * math.tan((zenith_list[i] - args.camera_zenith)/180.0*math.pi)
        if args.camera_azimuth > 90 and args.camera_azimuth < 270:
            yi = -yi
        if xi < -args.sensor_width/2 or xi > args.sensor_width/2 or yi < -args.sensor_height/2 or yi > args.sensor_height/2:
            continue
        if i == args.npoints_before - 1:
            colors.append("#ff0000")
        elif i == args.npoints_before:
            colors.append("#00ff00")
        elif i == args.npoints_before + 1:
            colors.append("#0000ff")
        else:
            colors.append("#ffff00")
        xs.append(xi)
        ys.append(yi)
    return xs,ys,colors

def plot(args, xs, ys, colors):
    fig, ax = plt.subplots()
    sun_in_mm = 1.392/149.6*args.focus_length
    sun_in_dots = sun_in_mm/args.sensor_width*fig.get_size_inches()[0]*fig.get_dpi()

    ax.scatter(xs, ys, sun_in_dots*sun_in_dots, colors)
    ax.set_xbound(-args.sensor_width/2, args.sensor_width/2)
    ax.set_ybound(-args.sensor_height/2, args.sensor_height/2)
    ax.set_xlabel('x/mm')
    ax.set_ylabel('y/mm')
    if args.save:
        plt.savefig(args.save)
    else:
        plt.show()

def main():
    default_latitude, default_longitude = getLatLon()
    parser = argparse.ArgumentParser()
    parser.description = "draw analemma, the Sun runs from red point to green point to blue point"
    parser.add_argument("--camera_azimuth", default=-1, help="azimuth of camera pointing to, the angle is 0 at north and positive towards the east", type=float)
    parser.add_argument("--camera_zenith", default=-1, help="zenith of camera pointing to, the angle is 0 at vertical and positive towards the horizon", type=float)
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
    if args.camera_azimuth == -1 or args.camera_zenith == -1:
        azimuth_list,zenith_list = getAzimuthZenithList(args)
        default_azimuth = sum(azimuth_list)/len(azimuth_list)
        default_zenith = sum(zenith_list)/len(zenith_list)
        if args.camera_azimuth == -1:
            args.camera_azimuth = default_azimuth
            print "default camera_azimuth is %f" % args.camera_azimuth
        if args.camera_zenith == -1:
            args.camera_zenith = default_zenith
            print "default camera_zenith is %f" % args.camera_zenith
    xs, ys, colors = getXYs(args)
    plot(args, xs, ys, colors)

if __name__ == "__main__":
    main()
