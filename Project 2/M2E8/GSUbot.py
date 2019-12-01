#!/usr/bin/env python3

import easygopigo3
import picamera
import numpy as np
from PIL import Image
from di_sensors import inertial_measurement_unit
import math

class Robot():
    def __init__(self):
        self.api_easy = easygopigo3.EasyGoPiGo3()
        self.hardware = self.Hardware(self.api_easy)
        self.firmware = self.Firmware(self.api_easy)
        self.vitals = self.Vitals(self.api_easy)
        self.distance = self.Distance( self.Servo( self.api_easy, "SERVO1" ) )
        self.camera = self.Camera( self.Servo( self.api_easy, "SERVO2" ) )
        self.imu = self.IMU(self.api_easy)
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
    def spin( self, degrees=360, speed = None ):
        if speed: self.api_easy.set_speed(speed)
        self.api_easy.turn_degrees( degrees )
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
                ", regulator_volts="+str(self.regulator_volts)+"V"+
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
    class Distance():
        def __init__( self, servo ):
            self.servo = servo
        @property
        def aim(self): return self.servo.aim
        @aim.setter
        def aim( self, degrees ): self.servo.aim = degrees
    class Camera():
        def __init__( self, servo ):
            self.api_camera = picamera.PiCamera()
            self.api_camera.resolution = (640, 480)
            self.api_camera.vflip = True
            self.api_camera.hflip = True
            self.api_camera.framerate = 25 ## API doesn't save framerate in file, players use 25 as default
            self.raw_image_array = np.empty((480, 640, 3), dtype = np.uint8)
            self.servo = servo
        @property
        def image(self):
            self.api_camera.capture( self.raw_image_array, format = 'rgb', use_video_port = True )  ## updates self.raw_image_array
            return Image.fromarray( self.raw_image_array )
        def record( self, filename, seconds ):
            self.api_camera.start_recording( filename, format='h264' ) ## TODO: actually get a constant framerate OR use a format that allows a variable framerate
            self.api_camera.wait_recording( seconds )
            self.api_camera.stop_recording()
            ## TODO: return an object that accepts .stop so we can make a recording of non-predetermined duration
        @property
        def aim(self): return self.servo.aim
        @aim.setter
        def aim( self, degrees ): self.servo.aim = degrees
    class IMU():
        def __init__(self,api_easy):
            self.api_easy = api_easy
            self.api_imu = inertial_measurement_unit.InertialMeasurementUnit(bus = "GPG3_AD1")
        @property
        def calibration_level(self):
            return self.api_imu.BNO055.get_calibration_status()[3]
        @property
        def heading(self):
            forward, upward, rightward = self.api_imu.read_magnetometer()
            ## Use x and -z according to sensor mount orientation: x is forward, y is up, and z is right
            heading = -math.atan2( rightward, forward ) * 180 / math.pi
            ## adjust to within -180 to 180
            if heading < -180:
                heading += 360
            elif heading > 180:
                heading -= 360
            ## Heading 0 is north, west is negative, east is positive, south is ±180
            # print( "forward: ", forward, "\trightward: ", rightward, "\theading: ", heading )
            return heading
    class Servo():
        def __init__( self, api_easy, servo_id ):
            self.api_easy = api_easy
            self.servo_id = servo_id
            self.api_servo = self.api_easy.init_servo(servo_id)
            self.raw_angle = None
            self.center_angle = None
        @property
        def aim(self): return self.center_angle
        @aim.setter
        def aim( self, degrees ):
            if degrees is False:  ## Spin "freely" with external forces (it's not actually free, but forcing it to turn won't do any harm)
                # print( "SERVO -- id =",self.servo_id,",\tDISABLED" )
                self.api_servo.disable_servo()  ##  TODO: read servo position after moved externally
            else:
                self.center_angle = min( max( -84, degrees ), 84 )  ##  TODO: initialize robot with angle offset and margins
                self.raw_angle = 90 - self.center_angle
                # print( "SERVO -- id =",self.servo_id,",\taim =",self.center_angle,",\traw = ",self.raw_angle )
                self.api_servo.rotate_servo( self.raw_angle )

    def __repr__(self):
        return ( "<"+
            type(self).__name__+"@"+hex(id(self))+
            ": api_easy="+str(self.api_easy)+
            ", hardware="+str(self.hardware)+
            ", firmware="+str(self.firmware)+
            ", vitals="+str(self.vitals)+
        ">" )

    
if __name__ == "__main__":
    robot = Robot()
    print( robot.hardware, robot.firmware, robot.vitals )
    delta = 5
    θ = 0
    while θ < 360:
        print( "Heading: ", robot.imu.heading )
        robot.spin( delta )
        θ += delta
    robot.imu.heading