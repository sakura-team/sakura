#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Started by Michael ORTEGA - 20/Sept/2018

import math
import numpy as np

def intersection(p1,p2,v1,v2):
    beta = (p1[1] + (p2[0]-p1[0])*v1[1]/v1[0] - p2[1])/(v2[1] - v2[0]*v1[1]/v1[0])
    return [x+beta*y for x,y in zip(p1,v1)]

def cross(v1,v2):
    return [v1[1]*v2[2]-v1[2]*v2[1],
            v1[2]*v2[0]-v1[0]*v2[2],
            v1[0]*v2[1]-v1[1]*v2[0]]

def dot(v1,v2):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def normalize(v):
    try:
        n = np.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    except ValueError:
        print()
        print()
        print(ValueError)
        print()
        exit(0)
    if n == 0:
        return [0,0,0]
    return [v[0]/n, v[1]/n, v[2]/n]

def norme(v):
    return math.sqrt(v[0]*v[0] + v[1]+v[1] + v[2]*v[2])

def m_mult(a, b):
    i, j = 0, 0
    M = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    while i < 4:
        while j < 4:
            M[i*4 + j] = a[i*4]*b[j] + a[i*4+1]*b[j+4] + a[i*4+2]*b[j+8] + a[i*4+3]*b[j+12]
            j += 1
        i += 1
        j = 0

    return M

def m_rotation(vector, angle):
    v = normalize(vector)
    s = math.sin(angle)
    c = math.cos(angle)
    C = 1 - c

    sx = s * v[0]
    sy = s * v[1]
    sz = s * v[2]
    Cx = C * v[0]
    Cy = C * v[1]
    Cz = C * v[2]
    Cxy = Cy * v[0]
    Cyz = Cz * v[1]
    Czx = Cx * v[2]

    return np.array([v[0] * Cx + c,      Cxy - sz,       Czx + sy,       0.0,
                       Cxy + sz,            v[1] * Cy + c,  Cyz - sx,       0.0,
                       Czx - sy,            Cyz + sx,       v[2] * Cz + c,  0.0,
                       0.0,                 0.0,            0.0,            1.0]).reshape((4,4))


def rotate(p, vector, angle, pivot = []):

    M = m_rotation(vector, angle)

    if len(pivot) == 0:
        return M.dot(np.array([p[0], p[1], p[2], 1.0]))[:3]
    else:
        po = np.array([p[0], p[1], p[2], 1.0])
        pi = np.array([pivot[0], pivot[1], pivot[2], 1.0])
        return (M.dot( po - pi) +pi)[:3]




def projectPointOnPlane(p0,p,n):
    """    This function gives the projection of p0 on the plan defined by a point ( p ) and a normal vector ( n )
        We suppose that norme(n) == 1"""

    #Normal of the triangle plan
    pp0         = [x-y for x,y in zip(p0,p)]
    pp0_norme     = norme(pp0)

    if pp0_norme == 0:
        return p

    #Angle between the normal and T[0]p
    pp0 = [x/pp0_norme for x in pp0]
    cosAlpha = dot(pp0,n)

    #Now the point on the plan
    return [x-(pp0_norme*cosAlpha)*y for x,y in zip(p0,n)]


class projector:
    """Parametres extrinseques et intrinseques d'un projecteur"""
    def __init__(self, position = [1000, 1000, 1000], width = 800, height = 600):
        self.position       = position
        self.viewpoint      = [0, 0, 0]
        self.direction      = None
        self.up             = [0, 1, 0]
        self.near           = 1
        self.far            = 1000
        self.width          = width
        self.height         = height
        self.v_angle        = 45*math.pi/180.0          #60degrees

        self.change_ratio(width/height)

    def change_ratio(self, new_ratio):
        self.ratio = new_ratio
        h = self.near*math.tan(self.v_angle/2.0)
        w = h*self.ratio

        self.left   = -w
        self.right  = w
        self.top    = h
        self.bottom = -h

    def read(self, f_name):
        """Reads projector params from a file which name is f_name"""
        print('\tReading proj calib...\t', end='')
        f = open(f_name,'r')

        self.near    = float((f.readline()).split(" ")[2])
        self.far     = float((f.readline()).split(" ")[2])
        self.left    = float((f.readline()).split(" ")[2])/self.near
        self.right   = float((f.readline()).split(" ")[2])/self.near
        self.bottom  = float((f.readline()).split(" ")[2])/self.near
        self.top     = float((f.readline()).split(" ")[2])/self.near
        self.near = 1

        tab     = f.readline().split(" ")
        pos     = [ float(tab[2]), float(tab[3]), float(tab[4]) ]

        tab     = f.readline().split(" ")
        vp      = [ float(tab[2]), float(tab[3]), float(tab[4]) ]

        tab     = f.readline().split(" ")
        up      = [ float(tab[2]), float(tab[3]), float(tab[4]) ]


        self.position   = pos
        self.viewpoint  = vp
        self.up         = up

        f.close()

        self.compute_direction()
        print('Ok')

    def compute_direction(self):
        self.direction = normalize([x-y for x, y in zip(self.viewpoint, self.position)])

    def print_params(self):
        print("Projector params :")
        print("\tNear               : ",self.near)
        print("\tFar                : ",self.far)
        print("\tPosition           : ",self.position)
        print("\tDirection          : ",self.direction)
        print("\tUp                 : ",self.up)
        print("\tFrustum(l,r,t,b)   : ",self.left, self.right, self.top, self.bottom)

    def projection(self):
        '''
        M=  [2n/(r-l)   0           (r+l)/(r-l)     0]
            [0          2n/(t-b)    (t+b)/(t-b)     0]
            [0          0           -(f+n)/(f-n)    -2(fn)/(f-n)]
            [0          0           -1              0]
        '''

        m00 = 2*self.near/(self.right - self.left)
        m02 = (self.right + self.left)/(self.right - self.left)
        m11 = 2*self.near/(self.top - self.bottom)
        m12 = (self.top + self.bottom)/(self.top - self.bottom)
        m22 = -(self.far+self.near)/(self.far-self.near)
        m23 = -2*(self.far*self.near)/(self.far-self.near)

        return np.array([   m00,   0,      m02,    0,
                            0,     m11,    m12,    0,
                            0,     0,      m22,    m23,
                            0,     0,      -1,     0  ]).reshape((4,4))

    def modelview(self):
        f   = normalize([   self.viewpoint[0] - self.position[0],
                            self.viewpoint[1] - self.position[1],
                            self.viewpoint[2] - self.position[2]  ])

        _up = normalize(self.up)
        s = cross(f, _up)
        u = cross(normalize(s), f)
        R = [   s[0],   u[0],   -f[0],  0,
                s[1],   u[1],   -f[1],  0,
                s[2],   u[2],   -f[2],  0,
                0,      0,      0,      1   ]

        T = [   1,      0,      0,      0,
                0,      1,      0,      0,
                0,      0,      1,      0,
                -self.position[0],-self.position[1],-self.position[2], 1 ]

        return np.array(m_mult(T, R)).reshape((4,4)).T

    def viewport(self):
        '''
        M=  [w/2        0           0               sx + w/2]
            [0          h/2         0               sy + h/2]
            [0          0           (f-n)/2         (f+n)/2]
            [0          0           0               1]
        Warning !!! Here we consider that we use the whole screen, so sx = sy = 0
        '''
        '''
        m00 = self.width/2.0
        m03 = 0 + self.width/2.0
        m11 = self.height/2.0
        m13 = 0 + self.height/2.0
        m22 = (self.far - self.near)/2.0
        m23 = (self.far + self.near)/2.0
        return np.array([   m00,   0,      0,       m03,
                            0,     m11,    0,       m13,
                            0,     0,      m22,     m23,
                            0,     0,      0,       1  ]).reshape((4,4)).T
        '''
        return np.array([   1,      0,      0,      0,
                            0,      1,      0,      0,
                            0,      0,      1,      0,
                            0,      0,      0,      1  ])


    def rotate_h(self, v):
        '''Horizontal rotation around viewpoint, v in radians'''
        self.position = rotate(self.position, self.up, v, pivot = self.viewpoint)


    def rotate_v(self, v):
        '''Vertical rotation around viewpoint, v in radians'''
        self.compute_direction()
        x = normalize(cross(self.direction, self.up))
        self.position = rotate(self.position, x, v, pivot = self.viewpoint)

        self.compute_direction()
        self.up = normalize(cross(x, self.direction))
