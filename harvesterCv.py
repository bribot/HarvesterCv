import cv2
import numpy as np
#import time
from harvesters.core import Harvester
from harvesters.util.pfnc import mono_location_formats, \
    rgb_formats, bgr_formats, \
    rgba_formats, bgra_formats

class Adquisition(Harvester):
    def __init__(self):
        self.h = Harvester()
        #self.h.add_file("../mvGenTLProducer.cti",True,True)
        self.h.add_file("../baumer/lib/libbgapi2_gige.cti")
        self.h.update()

    def getDevices(self):
        print(self.h.device_info_list)

    def setAdquisitionDevice(self,deviceId):
        print(f'Connecting to device referenced by:  {deviceId}')
        self.cam = self.h.create(deviceId)

    def setExposure(self,exposure):
        self.cam.remote_device.node_map.ExposureTime.set_value(exposure)
        exp = self.cam.remote_device.node_map.ExposureTime.value
        print("Exposure time set to ", exp)

    def setGain(self,gain):
        self.cam.remote_device.node_map.Gain.set_value(gain)
        val = self.cam.remote_device.node_map.Gain.value
        print("Gain set to ", val)
    
    def setTrigger(self, triggerVal):
        self.cam.remote_device.node_map.TriggerMode.value = triggerVal
        val = self.cam.remote_device.node_map.TriggerMode.value
        print("Trigger set ", val)

    def softwareTrigger(self):
        self.cam.remote_device.node_map.TriggerSoftware.execute()


    def startAdquisition(self):
        self.cam.start()
    
    def release(self):
        self.cam.stop()
    
    def read(self):
        buffer = self.cam.fetch()
        #print(buffer)
        payload = buffer.payload
        component = payload.components[0]
        width = component.width
        height = component.height
        data_format = component.data_format
        # Reshape the image so that it can be drawn on the VisPy canvas:
        if data_format in mono_location_formats:
            content = component.data.reshape(height, width,-1)
            content = np.dstack((content, content,content))
           
        else:
            # The image requires you to reshape it to draw it on the
            # canvas:
            if data_format in rgb_formats or \
                    data_format in rgba_formats or \
                    data_format in bgr_formats or \
                    data_format in bgra_formats:
                #
                content = component.data.reshape(
                    height, width,
                    int(component.num_components_per_pixel)  # Set of R, G, B, and Alpha
                )
                #
                if data_format in bgr_formats:
                    # Swap every R and B:
                    content = content[:, :, ::-1]
        #copy content into a new array since queue() destroys it
        frame = content.copy()
        #Queue buffer for next frame
        buffer.queue()
        return (True,frame)
        
        
        



def test_run():
    cap = Adquisition()
    cap.getDevices()
    pass

def test():
    cap.setAdquisitionDevice({'serial_number': 'S1176510'})
    cap.setExposure(50000)
    cap.setGain(1)
    cap.setTrigger("On")
    cap.startAdquisition()
    scale_percent = 20 # percent of original size
    
    while(True):
            cap.softwareTrigger()
            ret,frame = cap.read()
            #print(frame.shape)
            height, width, layer = frame.shape
            width = int(width * scale_percent / 100)
            height = int(height * scale_percent / 100)
            dim = (width, height)
            # resize image
            resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
            cv2.imshow('feed',resized)
            if cv2.waitKey(100)&0xFF==ord('q'):
                break



if __name__ == '__main__':
    test_run()

# ia.remote_device.node_map.Width.value = 2048
# ia.remote_device.node_map.Height.value = 2000
# ia.remote_device.node_map.PixelFormat.value = 'RGB8'
# ia.remote_device.node_map.AcquisitionLineRate.set_value(15000)
# ia.remote_device.node_map.ExposureTime.set_value(50000)
# ia.remote_device.node_map.Gain.set_value(6)
# ia.remote_device.node_map.TriggerSelector.value = "FrameBurstStart"
# ia.remote_device.node_map.TriggerMode.value = "On"
# ia.remote_device.node_map.triggerFrameCount.set_value(1) # new
# ia.remote_device.node_map.TriggerSource.value = "Line2"
# ia.remote_device.node_map.TriggerActivation.value = "RisingEdge"
# ia.remote_device.node_map.TriggerDelay.set_value(0.0) # new
# ia.remote_device.node_map.triggerDelaySource.value = "lineTriggerSignal" # new

# ia.remote_device.node_map.LineSelector.value = "Line2"
# ia.remote_device.node_map.LineFormat.value = "SingleEnded"

# ia.remote_device.node_map.lineDetectionLevel.value = "Threshold_for_3V3"
# ia.remote_device.node_map.LineInverter.value = False 
# ia.remote_device.node_map.lineDebouncingPeriod.value = 0
# ia.remote_device.node_map.lineElectricalTermination.value = "Disabled"