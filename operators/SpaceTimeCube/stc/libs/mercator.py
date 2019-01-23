#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA - for STEAMER/LIG/CNRS- 16/01/2019

import math

EARTH_RADIUS = 6378137 #Earth radius in meters

def merc_x(lon):
  r_major=6378137.000
  return r_major*math.radians(lon)

def merc_y(lat):
  if lat>89.5:lat=89.5
  if lat<-89.5:lat=-89.5
  r_major=6378137.000
  r_minor=6356752.3142
  temp=r_minor/r_major
  eccent=math.sqrt(1-temp**2)
  phi=math.radians(lat)
  sinphi=math.sin(phi)
  con=eccent*sinphi
  com=eccent/2
  con=((1.0-con)/(1.0+con))**com
  ts=math.tan((math.pi/2-phi)/2)/con
  y=0-r_major*math.log(ts)
  return y

def mercator(lon, lat, ele=None):
    x = EARTH_RADIUS * math.radians(lon)
    y =  math.log(math.tan(math.pi/4.0 + lat * (math.pi/180.0)/2.0)) * EARTH_RADIUS
    if ele == None:
        return x, y
    return x, y, ele # lon:x, lat:y

def lonlat_from_mercator(x, y):
    lon = math.degrees(x/EARTH_RADIUS)
    lat = (math.atan(math.exp(y/EARTH_RADIUS)) - math.pi/4.0)/((math.pi/180.0)/2.0)
    return lon, lat
