# Analemma

![alt example2](https://raw.githubusercontent.com/weishuyin/analemma/master/img/example2.png "example2")

In astronomy, an analemma is a diagram showing the position of the Sun in the sky, as seen from a fixed location on Earth at the same mean solar time, as that position varies over the course of a year[1]. 

This python code can show you how to take photos of analemma. How to place your DSLR, where and when to take shot.

The green point means the location of the Sun based on the date&time you input. Sun runs from the red point to the blue point.

In this code, date&time is in UTC format. Latitude is positive for the Northern Hemisphere, longitude is positive for the Eastern Hemisphere. Camera's orientation is same as android's orientation defined in /hardware/libhardware/include/hardware/sensors.h:
```
/**
 * Definition of the axis
 * ----------------------
 *
 * This API is relative to the screen of the device in its default orientation,
 * that is, if the device can be used in portrait or landscape, this API
 * is only relative to the NATURAL orientation of the screen. In other words,
 * the axis are not swapped when the device's screen orientation changes.
 * Higher level services /may/ perform this transformation.
 *
 *   x<0         x>0
 *                ^
 *                |
 *    +-----------+-->  y>0
 *    |           |
 *    |           |
 *    |           |
 *    |           |   / z<0
 *    |           |  /
 *    |           | /
 *    O-----------+/
 *    |[]  [ ]  []/
 *    +----------/+     y<0
 *              /
 *             /
 *           |/ z>0 (toward the sky)
 *
 *    O: Origin (x=0,y=0,z=0)
 *
 *
 * SENSOR_TYPE_ORIENTATION
 * -----------------------
 * 
 * All values are angles in degrees.
 * 
 * Orientation sensors return sensor events for all 3 axes at a constant
 * rate defined by setDelay().
 *
 * azimuth: angle between the magnetic north direction and the Y axis, around 
 *  the Z axis (0<=azimuth<360).
 *      0=North, 90=East, 180=South, 270=West
 * 
 * pitch: Rotation around X axis (-180<=pitch<=180), with positive values when
 *  the z-axis moves toward the y-axis.
 *
 * roll: Rotation around Y axis (-90<=roll<=90), with positive values when
 *  the x-axis moves towards the z-axis.
```
You can put your phone and DSLR together, DSLR screen's width align to phone's width, DSLR screen's height align to phone's height, so you can get DSLR's orientation.

In some app, orientation may be -180.0<=azimuth<=180.0, -90<=pitch<=90, -180<=roll<=180, it's ok.

Sun position calculation is based on [s-bear/sun-position](https://github.com/s-bear/sun-position).

# Install
```
sudo pip install matplotlib pytz numpy
```

# Examples:

## Example1
```
python analemma.py
```
![alt example1](https://raw.githubusercontent.com/weishuyin/analemma/master/img/example1.png "example1")

## Example2
```
python analemma.py --datetime '2019-12-4 7:0:0' --latitude 30.0 --longitude 120.0 --focal_length=16
```
![alt example2](https://raw.githubusercontent.com/weishuyin/analemma/master/img/example2.png "example2")


# References
[1] Analemma <https://en.wikipedia.org/wiki/Analemma>
