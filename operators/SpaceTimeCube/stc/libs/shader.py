#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA - 07/April/2017

import sys, numpy as np

try:
    from OpenGL.GL      import *
    from OpenGL.GL      import shaders
except:
    print ('''ERROR: PyOpenGL not installed properly.''')

##GLOBALS
current_nb_of_attributs = 0

##CLASS
class shader:
    def __init__(self):
        global current_nb_of_attributs
        current_nb_of_attributs = 0

        self.sh                 = None
        self.attr_vertices      = None
        self.attr_colors        = None
        self.attr_texture       = None
        self.attr_normals       = None

        self.vertices           = np.array([[0,0,0], [0,0,0]])
        self.normals            = np.array([[0,1,0], [0,1,0]])
        self.textures           = np.array([[0,0], [0,0]])
        self.colors             = np.array([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])
        self.ids                = np.array([[0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]])

        self.display            = None
        self.update_uniforms    = None
        self.texture_id         = None
        self.update_texture     = None
        self.update_arrays      = None

        self.uniform_names      = []
        self.uniform_handlers    = []

    def update_projections(self, matp, matm):

        #projection * view * model
        unif_p = glGetUniformLocation(self.sh, "projection_mat")
        unif_m = glGetUniformLocation(self.sh, "modelview_mat")

        glUniformMatrix4fv(unif_p, 1, False, matp.T)
        glUniformMatrix4fv(unif_m, 1, False, matm.T)

    def set_uniform(self, name, value, type):
        w = None
        try:
            ind = self.uniform_names.index(name)
            w = self.uniform_handlers[ind]
        except:
            w = glGetUniformLocation(self.sh, name)
            self.uniform_names.append(name)
            self.uniform_handlers.append(w)

        if w == -1:
            print("Pb with getting uniform location: ", name, "does not correspond to an active uniform!!")
        elif w in [GL_INVALID_VALUE, GL_INVALID_OPERATION]:
            print("Pb with getting uniform for", name, ", error", w)
        else:
            if type == 'i':
                glUniform1i(w, value)
            elif type == 'f':
                glUniform1f(w, value)
            elif type == '3fv':
                glUniform3fv(w, 1, value)
            elif type == '4fv':
                glUniform4fv(w, 1, value)
            elif type == 'm4fv':
                glUniformMatrix4fv(w, 1, False, value)
            else:
                print("Error in setting Uniform: Unknown type")

def compile(path, type, version):
    try:
        with open(path, 'r') as f:
            shader = f.read()
    except:
        print('\n\n\t!!!!!!!!!!!!!!!!!!!!!!!!!')
        print('\t!!! Cannot read', path, '!!!')
        print('\t!!!!!!!!!!!!!!!!!!!!!!!!!\n')
        return None

    if version:
        shader = "#version "+str(int(version.replace('.', '')))+"\n\n"+shader

    vs = glCreateShader(type)
    glShaderSource(vs, shader)

    glCompileShader(vs)
    log = glGetShaderInfoLog(vs)
    if log:
        print('\n\n\t!!!!!!!!!!!!!!!!!!!!!!!!!')
        print('\t!!!Shader', path,': ', log)
        print('\t!!!!!!!!!!!!!!!!!!!!!!!!!\n')
        return None

    return vs


def create(vert_fname, geom_fname, frag_fname, attrib_indexes, attrib_names, version = None):

    #Reading Shaders
    if vert_fname:
        vs = compile(vert_fname, GL_VERTEX_SHADER, version)
        if not vs:
            sys.exit()

    if geom_fname:
        gs = compile(geom_fname, GL_GEOMETRY_SHADER, version)
        if not gs:
            sys.exit()

    if frag_fname:
        fs = compile(frag_fname, GL_FRAGMENT_SHADER, version)
        if not fs:
            sys.exit()

    sh = glCreateProgram()

    if vert_fname:
        glAttachShader(sh, vs)
    if geom_fname:
        glAttachShader(sh, gs)
    if frag_fname:
        glAttachShader(sh, fs)

    for i, n in zip(attrib_indexes, attrib_names):
        glBindAttribLocation(sh, i, n)

    glLinkProgram(sh)

    log = glGetProgramInfoLog(sh)
    if log :
        print('After Linking the shader program:\n', log)
        if b"ERROR" in log:
            return None

    log = glUseProgram(sh)
    if log :
        print('After using program:\n', log)
        if b"ERROR" in log:
            return None

    return sh


def bind(vbo, arr, attr, nb, type):
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, arr.astype('float32'), GL_DYNAMIC_DRAW)
    glVertexAttribPointer(attr, nb, type, GL_FALSE, 0, None)
    glEnableVertexAttribArray(attr)


def new_attribute_index():
    global current_nb_of_attributs
    current_nb_of_attributs += 1
    return current_nb_of_attributs - 1


def display_list(l):
    for d in l:
        glUseProgram(d.sh)
        d.display()
