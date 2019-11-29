import easygopigo3
import picamera
import numpy as np
from PIL import Image

class Robot():
    def __init__(self):
        self.api_easy = easygopigo3.EasyGoPiGo3()
        self.hardware = self.Hardware(self.api_easy)
        self.firmware = self.Firmware(self.api_easy)
        self.vitals = self.Vitals(self.api_easy)
        self.camera = self.Camera()
    def forward( self, speed=None, distance=None ):
        if speed == None and distance == None:
            self.api_easy.forward()
        elif distance == None:  ## speed ≠ None
            self.api_easy.set_motor_dps( self.api_easy.MOTOR_LEFT | self.api_easy.MOTOR_RIGHT, speed )
        elif speed == None:  ## distance ≠ None
            self.api_easy.drive_cm( distance ) ## TODO: is cm really the best units?
        else: ## speed and distance both given
            raise "Unimplemented"
    def left(self):
        self.api_easy.left()
    def right(self):
        self.api_easy.right()
    def backward(self):
        self.api_easy.backward()
    def stop(self):
        self.api_easy.stop()
    def reset_all(self):
        self.api_easy.reset_all()
    def eyes( self, both=None, left=None, right=None ):
        if left != None or right != None: raise "Unimplemented"
        if both == False:
            self.api_easy.close_eyes()
        else:
            self.api_easy.set_eye_color(both)
            self.api_easy.open_eyes()
        ## TODO: return previous eye colors
    def blinkers( self, both=None, left=None, right=None ):
        if left != None or right != None: raise "Unimplemented"
        if both == False:
            self.api_easy.blinker_off("left")
            self.api_easy.blinker_off("right")
        elif both == True:
            self.api_easy.blinker_on("left")
            self.api_easy.blinker_on("right")
        ## TODO: return previous blinker states
    def motor_status( self, side ):
        id = None
        if side == "left":
            id = self.api_easy.MOTOR_LEFT
        elif side == "right":
            id = self.api_easy.MOTOR_RIGHT
        if id:
            return self.MotorStatus( self.api_easy.get_motor_status(id) )
    def odometer_read(self):
        return self.api_easy.read_encoders_average()
    def odometer_reset(self):
        self.api_easy.reset_encoders()
        ## TODO: return previous values
    class Hardware():
        def __init__(self,api_easy):
            self.api_easy = api_easy
        @property
        def manufacturer(self):
            return self.api_easy.get_manufacturer()
        @property
        def model(self):
            return self.api_easy.get_board()
        @property
        def version(self):
            return self.api_easy.get_version_hardware()
        @property
        def serial(self):
            return self.api_easy.get_id()
        def __repr__(self):
            return ( "<"+
                type(self).__name__+"@"+hex(id(self))+
                ": api_easy="+str(self.api_easy)+
                ", manufacturer="+str(self.manufacturer)+
                ", model="+str(self.model)+
                ", version="+str(self.version)+
                ", serial="+str(self.serial)+
            ">" )
    class Firmware():
        def __init__(self,api_easy):
            self.api_easy = api_easy
        @property
        def version(self):
            return self.api_easy.get_version_firmware()
        def __repr__(self):
            return ( "<"+
                type(self).__name__+"@"+hex(id(self))+
                ": api_easy="+str(self.api_easy)+
                ", version="+str(self.version)+
            ">" )
    class Vitals():
        def __init__(self,api_easy):
            self.api_easy = api_easy
        @property
        def battery_volts(self):
            return self.api_easy.get_voltage_battery()
        @property
        def regulator_volts(self):
            return self.api_easy.get_voltage_5v()
        def __repr__(self):
            return ( "<"+
                type(self).__name__+"@"+hex(id(self))+
                ": api_easy="+str(self.api_easy)+
                ", battery_volts="+str(self.battery_volts)+"V"+
                ", regulator_volts="+str(self.battery_volts)+"V"+
            ">" )
    class MotorStatus():
        def __init__( self, status ): ## see https://github.com/DexterInd/BrickPi3/blob/master/Software/Python/brickpi3.py#L939
            self.flags = status[0] ## 8-bits of bit-flags that indicate motor status
            self.power = status[1] ## raw PWM power in percent (-100 to 100)
            self.traveled = status[2] ## encoder position (changes with rotation)
            self.speed = status[3] ## current speed in Degrees Per Second
        def __repr__(self):
            return ( "<"+
                type(self).__name__+"@"+hex(id(self))+
                ": flags="+str(self.flags)+
                ", power="+str(self.power)+
                ", odometer="+str(self.traveled)+
                ", speed="+str(self.speed)+
            ">" )
        def __str__(self):
            return ( "("+
                " flags="+str(self.flags)+
                ", power="+str(self.power)+
                ", odometer="+str(self.traveled)+
                ", speed="+str(self.speed)+
            " )" )
    class Camera():
        def __init__(self):
            self.api_camera = picamera.PiCamera()
            self.api_camera.resolution = (640, 480)
            self.api_camera.vflip = True
            self.raw_image_array = np.empty((480, 640, 3), dtype = np.uint8)
        @property
        def image(self):
            self.api_camera.capture( self.raw_image_array, format = 'rgb', use_video_port = True )  ## updates self.raw_image_array
            return Image.fromarray( self.raw_image_array )
    def __repr__(self):
        return ( "<"+
            type(self).__name__+"@"+hex(id(self))+
            ": api_easy="+str(self.api_easy)+
            ", hardware="+str(self.hardware)+
            ", firmware="+str(self.firmware)+
            ", vitals="+str(self.vitals)+
        ">" )

    
