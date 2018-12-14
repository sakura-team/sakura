from sakura.common.gpu.libegl.devices.generic import GenericEGLDevice
from sakura.common.gpu.libegl.devices.gbm import GBMDevice

def probe():
    for cls in (GenericEGLDevice, GBMDevice):
        for device in cls.probe():
            yield device
