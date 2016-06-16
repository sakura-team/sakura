'''Autogenerated by get_gl_extensions script, do not edit!'''
from OpenGL import platform as _p, constants as _cs, arrays
from OpenGL.GL import glget
import ctypes
EXTENSION_NAME = 'GL_VERSION_GL_1_3'
def _f( function ):
    return _p.createFunction( function,_p.GL,'GL_VERSION_GL_1_3',False)
_p.unpack_constants( """GL_TEXTURE0 0x84C0
GL_TEXTURE1 0x84C1
GL_TEXTURE2 0x84C2
GL_TEXTURE3 0x84C3
GL_TEXTURE4 0x84C4
GL_TEXTURE5 0x84C5
GL_TEXTURE6 0x84C6
GL_TEXTURE7 0x84C7
GL_TEXTURE8 0x84C8
GL_TEXTURE9 0x84C9
GL_TEXTURE10 0x84CA
GL_TEXTURE11 0x84CB
GL_TEXTURE12 0x84CC
GL_TEXTURE13 0x84CD
GL_TEXTURE14 0x84CE
GL_TEXTURE15 0x84CF
GL_TEXTURE16 0x84D0
GL_TEXTURE17 0x84D1
GL_TEXTURE18 0x84D2
GL_TEXTURE19 0x84D3
GL_TEXTURE20 0x84D4
GL_TEXTURE21 0x84D5
GL_TEXTURE22 0x84D6
GL_TEXTURE23 0x84D7
GL_TEXTURE24 0x84D8
GL_TEXTURE25 0x84D9
GL_TEXTURE26 0x84DA
GL_TEXTURE27 0x84DB
GL_TEXTURE28 0x84DC
GL_TEXTURE29 0x84DD
GL_TEXTURE30 0x84DE
GL_TEXTURE31 0x84DF
GL_ACTIVE_TEXTURE 0x84E0
GL_MULTISAMPLE 0x809D
GL_SAMPLE_ALPHA_TO_COVERAGE 0x809E
GL_SAMPLE_ALPHA_TO_ONE 0x809F
GL_SAMPLE_COVERAGE 0x80A0
GL_SAMPLE_BUFFERS 0x80A8
GL_SAMPLES 0x80A9
GL_SAMPLE_COVERAGE_VALUE 0x80AA
GL_SAMPLE_COVERAGE_INVERT 0x80AB
GL_TEXTURE_CUBE_MAP 0x8513
GL_TEXTURE_BINDING_CUBE_MAP 0x8514
GL_TEXTURE_CUBE_MAP_POSITIVE_X 0x8515
GL_TEXTURE_CUBE_MAP_NEGATIVE_X 0x8516
GL_TEXTURE_CUBE_MAP_POSITIVE_Y 0x8517
GL_TEXTURE_CUBE_MAP_NEGATIVE_Y 0x8518
GL_TEXTURE_CUBE_MAP_POSITIVE_Z 0x8519
GL_TEXTURE_CUBE_MAP_NEGATIVE_Z 0x851A
GL_PROXY_TEXTURE_CUBE_MAP 0x851B
GL_MAX_CUBE_MAP_TEXTURE_SIZE 0x851C
GL_COMPRESSED_RGB 0x84ED
GL_COMPRESSED_RGBA 0x84EE
GL_TEXTURE_COMPRESSION_HINT 0x84EF
GL_TEXTURE_COMPRESSED_IMAGE_SIZE 0x86A0
GL_TEXTURE_COMPRESSED 0x86A1
GL_NUM_COMPRESSED_TEXTURE_FORMATS 0x86A2
GL_COMPRESSED_TEXTURE_FORMATS 0x86A3
GL_CLAMP_TO_BORDER 0x812D
GL_CLIENT_ACTIVE_TEXTURE 0x84E1
GL_MAX_TEXTURE_UNITS 0x84E2
GL_TRANSPOSE_MODELVIEW_MATRIX 0x84E3
GL_TRANSPOSE_PROJECTION_MATRIX 0x84E4
GL_TRANSPOSE_TEXTURE_MATRIX 0x84E5
GL_TRANSPOSE_COLOR_MATRIX 0x84E6
GL_MULTISAMPLE_BIT 0x20000000
GL_NORMAL_MAP 0x8511
GL_REFLECTION_MAP 0x8512
GL_COMPRESSED_ALPHA 0x84E9
GL_COMPRESSED_LUMINANCE 0x84EA
GL_COMPRESSED_LUMINANCE_ALPHA 0x84EB
GL_COMPRESSED_INTENSITY 0x84EC
GL_COMBINE 0x8570
GL_COMBINE_RGB 0x8571
GL_COMBINE_ALPHA 0x8572
GL_SOURCE0_RGB 0x8580
GL_SOURCE1_RGB 0x8581
GL_SOURCE2_RGB 0x8582
GL_SOURCE0_ALPHA 0x8588
GL_SOURCE1_ALPHA 0x8589
GL_SOURCE2_ALPHA 0x858A
GL_OPERAND0_RGB 0x8590
GL_OPERAND1_RGB 0x8591
GL_OPERAND2_RGB 0x8592
GL_OPERAND0_ALPHA 0x8598
GL_OPERAND1_ALPHA 0x8599
GL_OPERAND2_ALPHA 0x859A
GL_RGB_SCALE 0x8573
GL_ADD_SIGNED 0x8574
GL_INTERPOLATE 0x8575
GL_SUBTRACT 0x84E7
GL_CONSTANT 0x8576
GL_PRIMARY_COLOR 0x8577
GL_PREVIOUS 0x8578
GL_DOT3_RGB 0x86AE
GL_DOT3_RGBA 0x86AF""", globals())
glget.addGLGetConstant( GL_ACTIVE_TEXTURE, (1,) )
glget.addGLGetConstant( GL_MULTISAMPLE, (1,) )
glget.addGLGetConstant( GL_SAMPLE_ALPHA_TO_COVERAGE, (1,) )
glget.addGLGetConstant( GL_SAMPLE_ALPHA_TO_ONE, (1,) )
glget.addGLGetConstant( GL_SAMPLE_COVERAGE, (1,) )
glget.addGLGetConstant( GL_SAMPLE_BUFFERS, (1,) )
glget.addGLGetConstant( GL_SAMPLES, (1,) )
glget.addGLGetConstant( GL_SAMPLE_COVERAGE_VALUE, (1,) )
glget.addGLGetConstant( GL_SAMPLE_COVERAGE_INVERT, (1,) )
glget.addGLGetConstant( GL_TEXTURE_CUBE_MAP, (1,) )
glget.addGLGetConstant( GL_TEXTURE_BINDING_CUBE_MAP, (1,) )
glget.addGLGetConstant( GL_MAX_CUBE_MAP_TEXTURE_SIZE, (1,) )
glget.addGLGetConstant( GL_TEXTURE_COMPRESSION_HINT, (1,) )
glget.addGLGetConstant( GL_NUM_COMPRESSED_TEXTURE_FORMATS, (1,) )
glget.addGLGetConstant( GL_COMPRESSED_TEXTURE_FORMATS, (1,) )
glget.addGLGetConstant( GL_CLIENT_ACTIVE_TEXTURE, (1,) )
glget.addGLGetConstant( GL_MAX_TEXTURE_UNITS, (1,) )
glget.addGLGetConstant( GL_TRANSPOSE_MODELVIEW_MATRIX, (4,4) )
glget.addGLGetConstant( GL_TRANSPOSE_PROJECTION_MATRIX, (4,4) )
glget.addGLGetConstant( GL_TRANSPOSE_TEXTURE_MATRIX, (4,4) )
glget.addGLGetConstant( GL_TRANSPOSE_COLOR_MATRIX, (4,4) )
@_f
@_p.types(None,_cs.GLenum)
def glActiveTexture( texture ):pass
@_f
@_p.types(None,_cs.GLfloat,_cs.GLboolean)
def glSampleCoverage( value,invert ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLint,_cs.GLenum,_cs.GLsizei,_cs.GLsizei,_cs.GLsizei,_cs.GLint,_cs.GLsizei,ctypes.c_void_p)
def glCompressedTexImage3D( target,level,internalformat,width,height,depth,border,imageSize,data ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLint,_cs.GLenum,_cs.GLsizei,_cs.GLsizei,_cs.GLint,_cs.GLsizei,ctypes.c_void_p)
def glCompressedTexImage2D( target,level,internalformat,width,height,border,imageSize,data ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLint,_cs.GLenum,_cs.GLsizei,_cs.GLint,_cs.GLsizei,ctypes.c_void_p)
def glCompressedTexImage1D( target,level,internalformat,width,border,imageSize,data ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLint,_cs.GLint,_cs.GLint,_cs.GLint,_cs.GLsizei,_cs.GLsizei,_cs.GLsizei,_cs.GLenum,_cs.GLsizei,ctypes.c_void_p)
def glCompressedTexSubImage3D( target,level,xoffset,yoffset,zoffset,width,height,depth,format,imageSize,data ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLint,_cs.GLint,_cs.GLint,_cs.GLsizei,_cs.GLsizei,_cs.GLenum,_cs.GLsizei,ctypes.c_void_p)
def glCompressedTexSubImage2D( target,level,xoffset,yoffset,width,height,format,imageSize,data ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLint,_cs.GLint,_cs.GLsizei,_cs.GLenum,_cs.GLsizei,ctypes.c_void_p)
def glCompressedTexSubImage1D( target,level,xoffset,width,format,imageSize,data ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLint,ctypes.c_void_p)
def glGetCompressedTexImage( target,level,img ):pass
@_f
@_p.types(None,_cs.GLenum)
def glClientActiveTexture( texture ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLdouble)
def glMultiTexCoord1d( target,s ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLdoubleArray)
def glMultiTexCoord1dv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLfloat)
def glMultiTexCoord1f( target,s ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLfloatArray)
def glMultiTexCoord1fv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLint)
def glMultiTexCoord1i( target,s ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLintArray)
def glMultiTexCoord1iv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLshort)
def glMultiTexCoord1s( target,s ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLshortArray)
def glMultiTexCoord1sv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLdouble,_cs.GLdouble)
def glMultiTexCoord2d( target,s,t ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLdoubleArray)
def glMultiTexCoord2dv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLfloat,_cs.GLfloat)
def glMultiTexCoord2f( target,s,t ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLfloatArray)
def glMultiTexCoord2fv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLint,_cs.GLint)
def glMultiTexCoord2i( target,s,t ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLintArray)
def glMultiTexCoord2iv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLshort,_cs.GLshort)
def glMultiTexCoord2s( target,s,t ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLshortArray)
def glMultiTexCoord2sv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLdouble,_cs.GLdouble,_cs.GLdouble)
def glMultiTexCoord3d( target,s,t,r ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLdoubleArray)
def glMultiTexCoord3dv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLfloat,_cs.GLfloat,_cs.GLfloat)
def glMultiTexCoord3f( target,s,t,r ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLfloatArray)
def glMultiTexCoord3fv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLint,_cs.GLint,_cs.GLint)
def glMultiTexCoord3i( target,s,t,r ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLintArray)
def glMultiTexCoord3iv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLshort,_cs.GLshort,_cs.GLshort)
def glMultiTexCoord3s( target,s,t,r ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLshortArray)
def glMultiTexCoord3sv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLdouble,_cs.GLdouble,_cs.GLdouble,_cs.GLdouble)
def glMultiTexCoord4d( target,s,t,r,q ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLdoubleArray)
def glMultiTexCoord4dv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLfloat,_cs.GLfloat,_cs.GLfloat,_cs.GLfloat)
def glMultiTexCoord4f( target,s,t,r,q ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLfloatArray)
def glMultiTexCoord4fv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLint,_cs.GLint,_cs.GLint,_cs.GLint)
def glMultiTexCoord4i( target,s,t,r,q ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLintArray)
def glMultiTexCoord4iv( target,v ):pass
@_f
@_p.types(None,_cs.GLenum,_cs.GLshort,_cs.GLshort,_cs.GLshort,_cs.GLshort)
def glMultiTexCoord4s( target,s,t,r,q ):pass
@_f
@_p.types(None,_cs.GLenum,arrays.GLshortArray)
def glMultiTexCoord4sv( target,v ):pass
@_f
@_p.types(None,arrays.GLfloatArray)
def glLoadTransposeMatrixf( m ):pass
@_f
@_p.types(None,arrays.GLdoubleArray)
def glLoadTransposeMatrixd( m ):pass
@_f
@_p.types(None,arrays.GLfloatArray)
def glMultTransposeMatrixf( m ):pass
@_f
@_p.types(None,arrays.GLdoubleArray)
def glMultTransposeMatrixd( m ):pass
