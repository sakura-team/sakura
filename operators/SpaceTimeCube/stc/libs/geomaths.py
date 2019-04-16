#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA - for STEAMER/LIG/CNRS- 29/01/2018

import numpy as np
import math, copy, random


def distance_2D(a, b):
    return math.sqrt(   (b[0]-a[0])**2 +
                        (b[1]-a[1])**2  )

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


def normalize(v):
    n = norm(v)
    if n != 0:
        for i in range(len(v)):
            v[i] /= n
        return v
    for i in range(len(v)):
        v[i] = 0
    return v

def vector(a, b):
    v = []
    for i in range(len(a)):
        v.append(b[i] - a[i])
    return v

def norm(v):
    n = 0
    for i in range(len(v)):
        n += v[i]*v[i]
    return math.sqrt(n)

def cross (u,v):
    return [u[1]*v[2] - u[2]*v[1],
            u[2]*v[0] - u[0]*v[2],
            u[0]*v[1] - u[1]*v[0]]

def dot(u, v):
    res = 0
    for i in range(len(u)):
        res += u[i]*v[i]
    return res

def perspective(fov, aspect, near, far):
    rfov = fov*math.pi/180.
    d = math.tan(rfov/2.0)
    mat = np.zeros((4,4))

    mat[0][0] = 1/(d*aspect)
    mat[1][1] = 1/d
    mat[2][2] = (near + far)/(near - far)
    mat[2][3] = 2*near*far/(near-far)
    mat[3][2] = -1

    return mat


def viewport(sx, sy, w, h, near, far):

    mat = np.identity(4)

    mat[0][0] = w/2.
    mat[0][3] = sx + w/2.
    mat[1][1] = h/2.
    mat[1][3] = sy + h/2.
    mat[2][2] = (far-near)/2.
    mat[2][3] = (far+near)/2.

    return mat


def orthographic(left, right, bottom, top, near, far):

    mat = np.identity(4)

    mat[0][0] = 2./(right-left)
    mat[0][3] = -(right+left)/(right-left)
    mat[1][1] = 2./(top-bottom)
    mat[1][3] = -(top+bottom)/(top-bottom)
    mat[2][2] = -2./(far-near)
    mat[2][3] = -(far+near)/(far-near)

    return mat


def look_at(eye, center, up):
    f = normalize([   center[0] - eye[0],
                        center[1] - eye[1],
                        center[2] - eye[2]  ])

    _up = normalize(up)
    s = cross(f, _up)
    u = cross(normalize(s), f)
    R = [   s[0],   u[0],   -f[0],  0,
            s[1],   u[1],   -f[1],  0,
            s[2],   u[2],   -f[2],  0,
            0,      0,      0,      1   ]

    T = [   1,      0,      0,      0,
            0,      1,      0,      0,
            0,      0,      1,      0,
            -eye[0],-eye[1],-eye[2], 1 ]

    return np.array(m_mult(T, R)).reshape((4,4)).T

def distances_point_frame(p, mins, maxs):
    ''' Frame is defined by two corners
        we suppose 'mins' is north-west '''
    vx = [1,0,0]
    vz = [0,0,1]
    v_mins = p - mins[0:3]
    v_maxs = p - maxs[0:3]
    w = norm(cross(v_mins, vz))
    e = norm(cross(v_maxs, vz))
    n = norm(cross(v_mins, vx))
    s = norm(cross(v_maxs, vx))

    return w, e, n, s

def cylinder(pos, radius, height, tess, color):
    a = 2*math.pi/tess
    h = np.array([0, 0, 0, height])

    vertices = np.empty([tess*12, 4])
    normals = np.empty([tess*12, 3])

    for i in range(tess):

        #vertices
        p1 = np.array([math.cos(i*a)*radius, 0, math.sin(i*a)*radius, 0]) + pos
        p2 = np.array([math.cos((i+1)*a)*radius, 0, math.sin((i+1)*a)*radius, 0]) + pos
        p3 = p2 + h
        p4 = p1 + h

        #normals
        n1 = normalize(p1[[0,3,2]] - pos[[0,3,2]])
        n2 = normalize(p2[[0,3,2]] - pos[[0,3,2]])
        n3 = normalize(p3[[0,3,2]] - (pos[[0,3,2]] + h[[0,3,2]]))
        n4 = normalize(p4[[0,3,2]] - (pos[[0,3,2]] + h[[0,3,2]]))
        nh = np.array([0,1,0])

        for v, n, j in zip([pos + h, p4, p3, p1, p2, p3, p1, p3, p4, pos, p1, p2],
                            [ nh, nh, nh, n1, n2, n3, n1, n3, n4, -nh, -nh, -nh],
                            range(12)):
            vertices[12*i + j] = v
            normals [12*i + j] = n
    colors   = np.full((len(vertices), 4), color)

    return vertices, normals, colors


def spiral(mat, seed):
    debug = True
    flat = [copy.copy(seed)]
    final = [mat[seed[0]][seed[1]]]
    w = len(mat)
    h = len(mat[0])
    N, S, W, E = (-1, 0), (1, 0), (0, -1), (0, 1) # directions
    turn_right = {N: E, E: S, S: W, W: N} # old -> new direction
    turn_back = {E: N, S: E, W: S, N: W}

    dir = N
    while len(flat) < w*h:
        seed[0] += dir[0]
        seed[1] += dir[1]

        #outside of the matrix
        if seed[0] >= w or seed[1] >= h or seed[0] < 0 or seed[1] < 0:
            seed[0] -= dir[0]
            seed[1] -= dir[1]
            dir = turn_right[dir]
            seed[0] += dir[0]
            seed[1] += dir[1]
        #still in the matrix, but already passed here
        elif seed in flat:
            seed[0] -= dir[0]
            seed[1] -= dir[1]
            dir = turn_back[dir]
        #here is good
        else:
            flat.append(copy.copy(seed))
            final.append(mat[seed[0]][seed[1]])
            dir = turn_right[dir]

    return final

def random_color():
    return np.array([   random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255)])/255.

def id_to_color(id):
    r = int(id/(255*255))
    v = int((id - r*(255*255))/255)
    b = (id - r*255*255 - v*255)
    return [r/255.0, v/255.0, b/255.0, 1.0]

def color_to_id(color):
    color *= 255
    return int(color[2] + color[1]*255 + color[0]*255*255)

def pt_in_frame(p, mins, maxs):
    if  p[0] >= mins[0] and \
        p[0] <= maxs[0] and \
        p[1] >= mins[1] and \
        p[1] <= maxs[1]:
        return True
    return False

def proj_pt_on_line(p, a, b):
    '''point: p; line defined by [a,b]'''
    ap, ab = [], []
    for i in range(len(p)):
        ap.append(p[i]-a[i])
        ab.append(b[i]-a[i])

    d = dot(ap,ab)/dot(ab,ab)
    res = []
    for i in range(len(p)):
        res.append(a[i] + d * ab[i])
    return res
