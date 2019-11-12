#!python3

import time     # import the time library for the sleep function
import gopigo3 # import the GoPiGo3 drivers
import easygopigo3
import picamera
from di_sensors import inertial_measurement_unit ## because di_sensors couldn't be bothered to make di_sensors.inertial_measurement_unit work

class ShadPiGo:
    DISTANCE_SERVO_OFFSET = 7 ## difference in degrees between servo orientation and body orientation
    CAMERA_SERVO_OFFSET = -18 ## difference in degrees between servo orientation and body orientation

    def __init__(self):  ## TODO: some of this should probably go in startup()?
        self.api_full = gopigo3.GoPiGo3() # Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.
        self.api_easy = easygopigo3.EasyGoPiGo3()
        self.active = False
        self.distance = self.api_easy.init_distance_sensor()
        self.distance_servo = self.api_easy.init_servo("SERVO1")
        self.camera = picamera.PiCamera()
        self.camera_servo = self.api_easy.init_servo("SERVO2")
        self.imu = inertial_measurement_unit.InertialMeasurementUnit(bus = "GPG3_AD1")

    def aimDistance( self, degrees_right = 0 ):
        try:
            control_angle = 90 + self.DISTANCE_SERVO_OFFSET - degrees_right
            print( "aimDistance( "+str(degrees_right)+" ): control_angle = "+str(control_angle) )
            self.distance_servo.rotate_servo( control_angle )  ## TODO: impose limits (don't strain motor); 0-?
        except Exception as e:
            print( "!!! EXCEPTION: "+repr(e) )        

    def aimCamera( self, degrees_right = 0 ):
        try:
            control_angle = 90 + self.CAMERA_SERVO_OFFSET - degrees_right
            print( "aimCamera( "+str(degrees_right)+" ): control_angle = "+str(control_angle) )
            self.camera_servo.rotate_servo( control_angle )  ## TODO: impose limits (don't strain motor); 6-?
        except Exception as e:
            print( "!!! EXCEPTION: "+repr(e) )

    def doPrepServos(self):
        print( "Prepping Servos" )
        self.aimDistance( 0 ) ## set distance servo to middle position (forward)
        self.aimCamera( 0 ) ## set camera servo to middle position (forward)
    def doParkServos(self):
        print( "Parking Servos" )
        self.aimDistance( 90 + self.DISTANCE_SERVO_OFFSET ) ## set distance servo to far right position
        self.aimCamera( 84 + self.CAMERA_SERVO_OFFSET ) ## set distance servo to far right position

    def startup(self):
        self.doPrepServos()
        self.active = True
        return self

    def shutdown(self):
        self.doParkServos()
        self.active = False
        self.api_easy.reset_all()
        self.api_full.reset_all()
        return self


print( "┏━━━━━━━━━┉┅╍╌" )

robot = ShadPiGo()

robot.startup()

robot.shutdown()

print( " ╌╍┅┉━━━━━━━━━┛" )
