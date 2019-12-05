# Analemma

In astronomy, an analemma is a diagram showing the position of the Sun in the sky, as seen from a fixed location on Earth at the same mean solar time, as that position varies over the course of a year[1]. 

This python code can show you how to take photos of analemma. How to place your DSLR, where and when to take shot.

In this code, the latitude and longitude are positive for North and East, respectively. The azimuth angle is 0 at North and positive towards the east. The zenith angle is 0 at vertical and positive towards the horizon[2]. 

The datetime must be in UTC.

The green point means where is Sun at the datetime you inputted. Sun runs from the red point to the blue point.

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
python analemma.py --datetime '2019-12-4 7:0:0' --latitude 30.0 --longitude 120.0 --focus_length=16 --camera_azimuth 250 --camera_zenith 70
```
![alt example12](https://raw.githubusercontent.com/weishuyin/analemma/master/img/example2.png "example2")


# References
[1] Analemma <https://en.wikipedia.org/wiki/Analemma>

[2] s-bear/sun-position <https://github.com/s-bear/sun-position>
