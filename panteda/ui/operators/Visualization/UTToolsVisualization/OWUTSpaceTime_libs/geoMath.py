## This library is made for vectors 3
## It has been made from code lines made by Renaud Blanch: http://iihm.imag.fr/blanch/


import math

#################################
## QUATERNIONS

def quaternion(theta=0, u=(1., 0., 0.)):
    w = math.cos(theta/2.)
    x, y, z = (ui*math.sin(theta/2.) for ui in u)
    return w, (x, y, z)

#################################
## MATRICES

def matrix(n, m, f=lambda i, j: 0.):
    I, J = range(n), range(m)
    return [[f(i, j) for j in J] for i in I]

def size(A):
	return len(A), len(A[0])
	
def matrixFromVector(v):
    return [[vi] for vi in v]

def matrixFromQuaternion(Q):
    w, (x, y, z) = Q
    return [[1.-2.*(y*y+z*z), 2.*(x*y+w*z),    2.*(x*z-w*y),    0.],
            [2.*(x*y-w*z),    1.-2.*(x*x+z*z), 2.*(y*z+w*x),    0.],
            [2.*(x*z+w*y),    2.*(y*z-w*x),    1.-2.*(x*x+y*y), 0.],
            [0.,              0.,              0.,              1.]]

def matrixSize(A):
    return len(A), len(A[0])

def multMatrices(A, B):
    n, p = matrixSize(A)
    q, m = matrixSize(B)
    assert p == q
    K = range( p )
    return matrix(n, m, lambda i, j: sum(A[i][k]*B[k][j] for k in K))


def transposeMatrix(m):
    M = matrix(4,4)
    for i in range(4): 
        for j in range(4):
            M[i][j] = m[j][i]
    return M
    
# inverse 

def exclude(A, i, j):
	return [R[:j]+R[j+1:] for R in A[:i]+A[i+1:]]

def scalar(s, A):
	n, m = size(A)
	return matrix(n, m, lambda i, j: s*A[i][j])
	
def det(A):
	n, m = size(A)
	assert n == m
	if n == 1:
		return A[0][0]
	else:
		return sum(A[i][0]*cofactor(A, i, 0) for i in range(n))

def minor(A, i, j):
	return det(exclude(A, i, j))

def cofactor(A, i, j):
	return (-1)**(i+j)*minor(A, i, j)

def inverseMatrix(A):
	n, m = size(A)
	assert n == m
	C = matrix(n, m, lambda i, j: cofactor(A, i, j))
	I = range(n)
	d = sum(A[i][0]*C[i][0] for i in I)
	return scalar(1./d, transposeMatrix(C))
	
#################################
## VECTORS
	    
def cross(v1,v2):
    return [v1[1]*v2[2]-v1[2]*v2[1],
            v1[2]*v2[0]-v1[0]*v2[2],
            v1[0]*v2[1]-v1[1]*v2[0]]
def dot(v1,v2):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
    
def normalize(v):
    res = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    if res == 0:
        return [0,0,0]
    else:
        return [x/res for x in v]
        
def rotatePointWithPivot(pos,q,p):
    #pivot in local frame
    pivot = p
		
    #rotation
    center 	= [x-y for x,y in zip(pos,pivot)]
    center 	= matrixFromVector(list(center)+[1.])
    M 		= matrixFromQuaternion(q)
    center 	= multMatrices(M,center)
    center 	= [center[i][0] for i in range(3)]
    center 	= [x+y for x,y in zip(center,pivot)]

    return center

def distance3DSquared(v1,v2):
    return  (v2[0]-v1[0])*(v2[0]-v1[0]) + \
            (v2[1]-v1[1])*(v2[1]-v1[1]) + \
            (v2[2]-v1[2])*(v2[2]-v1[2])
  
def distance2DSquared(v1,v2):
    return  (v2[0]-v1[0])*(v2[0]-v1[0]) + \
            (v2[1]-v1[1])*(v2[1]-v1[1])
            
def projectPointOnScreen(pt,m):
    if len(pt) < 4:
        pt.append(1.0)
    m_pt = matrixFromVector(pt)
    m_m  = multMatrices(m,m_pt)
    return [m_m[0][0]/m_m[3][0],m_m[1][0]/m_m[3][0]]
    

def projectPointOnLine(p,p_line,v):
    "This function computes the projection of p on the line defined by point p_line and vector v"
    nv = [x-y for x,y in zip(p,p_line)]
    alpha = dot(nv,v)

    return [x+alpha*y for x,y in zip(p_line,v)]
