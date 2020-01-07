# Analemma
  
![alt example2](https://raw.githubusercontent.com/weishuyin/analemma/master/img/example2.png "example2")  
  
In astronomy, an analemma is a diagram showing the position of the Sun in the sky, as seen from a fixed location on Earth at the same mean solar time, as that position varies over the course of a year[1].  
  
This python project contains two programs:
1. analemma.py: Simulate analemma photo based on GPS info, DSLR's orientation, DSLR's CMOS info.  
The green point means the location of the Sun based on the date&time you input. Sun runs from the red point to the blue point.  

2. orientation.py: Calculate DLSR's orientation based on GPS info, position of Sun in photo and corresponding datetime.  
  
To get DSLR's orientation, there are two methods:
1. Use sensor app on phone.  
	Put your phone and DSLR together, DSLR screen's width align to phone's width, DSLR screen's height align to phone's height. You can read orientation info from app.  
	In some app, orientation may be -180.0<=azimuth<=180.0, -180<=pitch<=180, -90<=roll<=90, it's ok.  
  
2. Use orientation.py.  
	Put your DSLR on tripod and keep it not be moved. Take some photos of the Sun every 30min or other interval. Run orientation.py and input the position(in pixel) of the Sun in photo and the corresponding datetime. We can get DSLR's orientation.  
  
In this code, date&time is in UTC format. Latitude is positive for the Northern Hemisphere, longitude is positive for the Eastern Hemisphere. DSLR's orientation is like android's orientation defined in /hardware/libhardware/include/hardware/sensors.h, but the range of pitch is -90.0\~90.0, the range of roll is -180.0\~180.0:
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
 * pitch: Rotation around X axis (-90<=pitch<=90), with positive values when
 *  the z-axis moves toward the y-axis.
 *
 * roll: Rotation around Y axis (-180<=roll<=180), with positive values when
 *  the x-axis moves towards the z-axis.
```
  
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
python analemma.py --camera_azimuth 56 --camera_pitch -53 --camera_roll 180 --focal_length 16 --sensor_width 36 --sensor_height 24 --pixel_width 5760 --pixel_height 3840 --datetime '2019-12-4 7:0:0' --latitude 30.0 --longitude 120.0 --elevation 0
```
![alt example2](https://raw.githubusercontent.com/weishuyin/analemma/master/img/example2.png "example2")

## Example3
```
python orientation.py --latitude 30.29 --longitude 120.16 --elevation 0 --data '[[4590,925,"2019-07-11 08:50:35"],[4440,1000,"2019-07-23 08:50:35"],[4255,1126,"2019-08-04 08:50:35"]]' --focal_length 24 --sensor_width 36 --sensor_height 24 --pixel_width 5760 --pixel_height 3840
```

# References
[1] Analemma <https://en.wikipedia.org/wiki/Analemma>
