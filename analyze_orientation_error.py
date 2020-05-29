#!/usr/bin/python

# how to fix camera orientation error:
# 1. put camera on tripod, lens torwards to sun
# 2. make sure of that camera_roll is about 0 or 180
# 3. change camera_azimuth and try different azimuth_error until delta_x&delta_y between real sun and calculated sun fixed
# 4. try different pitch_error until delta_y become zero
# 5. try different roll_error until delta_x become zero

from sunposition import sunpos
from datetime import datetime
import sys
import math
import numpy as np
import matplotlib.pyplot as plt

latitude = 40.0
longitude = 116.0
elevation = 0

focal_length = 35
sensor_width = 36
sensor_height = 24
facing_back = True

# utc
date = datetime.strptime('2020-5-29 4:00:00', '%Y-%m-%d %H:%M:%S')

def getSolarPosition(date):
    azimuth, zenith = sunpos(date, latitude=latitude, longitude=longitude, elevation=elevation)[:2]
    return azimuth, zenith

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

def getPoint(date, camera_azimuth, camera_pitch, camera_roll):
    azimuth, zenith = getSolarPosition(date)
    worldPoint = worldAzimuthZenith2WorldPoint(azimuth, zenith)
    viewPoint = worldPoint2ViewPoint(worldPoint, camera_azimuth, camera_pitch, camera_roll)
    projectionPoint = viewPoint2Projection(viewPoint, focal_length, sensor_width, sensor_height, facing_back)
    if not projectionPoint:
        print "out of range"
        return None
    print "x=%f y=%f" % (projectionPoint[0], projectionPoint[1])
    return projectionPoint

def plot(xs, ys, colors):
    fig, ax = plt.subplots()
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    sun_diameter_in_mm = 1.392/149.6*focal_length
    sun_diameter_in_dots = sun_diameter_in_mm/sensor_width*bbox.width*fig.get_dpi()

    ax.scatter(xs, ys, sun_diameter_in_dots*sun_diameter_in_dots, colors)
    ax.set_xbound(-sensor_width/2, sensor_width/2)
    ax.set_ybound(-sensor_height/2, sensor_height/2)
    ax.set_xlabel('x/mm')
    ax.set_ylabel('y/mm')
    ax.set_aspect('equal');
    plt.show()

camera_azimuth = 20
camera_pitch = -18
camera_roll = 170

delta = 1
npoints = 10

projectionPoints = []
colors = []

projectionPoint = getPoint(date, camera_azimuth, camera_pitch, camera_roll)
projectionPoints.append(projectionPoint)
colors.append("#00ff00")

for i in range(npoints):
    projectionPoint = getPoint(date, camera_azimuth+(i+1)*delta, camera_pitch, camera_roll)
    if projectionPoint:
        projectionPoints.append(projectionPoint)
        colors.append("#ff0000")

    projectionPoint = getPoint(date, camera_azimuth, camera_pitch+(i+1)*delta, camera_roll)
    if projectionPoint:
        projectionPoints.append(projectionPoint)
        colors.append("#0000ff")

    projectionPoint = getPoint(date, camera_azimuth, camera_pitch, camera_roll+(i+1)*delta)
    if projectionPoint:
        projectionPoints.append(projectionPoint)
        colors.append("#ffff00")

plot([point[0] for point in projectionPoints], [point[1] for point in projectionPoints], colors)
