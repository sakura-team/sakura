'''OpenGL extension SGIX.list_priority

This module customises the behaviour of the 
OpenGL.raw.GL.SGIX.list_priority to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension provides a mechanism for specifying the relative
	importance of display lists.  This information can be used by
	an OpenGL implementation to guide the placement of display
	list data in a storage hierarchy.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SGIX/list_priority.txt
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions, wrapper
from OpenGL.GL import glget
import ctypes
from OpenGL.raw.GL.SGIX.list_priority import *
### END AUTOGENERATED SECTION