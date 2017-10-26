﻿from abc import *
from config import *
from packets import *
import struct

class simpledevice():

    __metaclass__ = ABCMeta

    def __init__(self, deviceType):
        self.device = device.validate(deviceType)
        self.port = None
        self.index = None

    @abstractmethod
    def parseData(self, data):
        return False

    def bytesToFloat(self, s ,pos_start):
        d =bytearray(s[pos_start:pos_start+4])
        f = struct.unpack("1f",str(d))[0]
        return f

    def bytesToBool(self, s, pos_start):
        d =bytearray(s[pos_start:pos_start+1])
        c = struct.unpack("1c",str(d))[0]
        return c

class slotteddevice(simpledevice):

    __metaclass__ = ABCMeta

    def __init__(self, deviceType, moduleSlot):
        super(slotteddevice, self).__init__(deviceType)
        self.slot = slot.validate(moduleSlot)

class readabledevice():

    __metaclass__ = ABCMeta

    def __init__(self):
        self._value = -1
        self._millis = -1

    def requestValue(self):
        slot = None
        if hasattr(self, 'slot'):
            slot = self.slot
        self.port.sendRequest(requestpacket(self.index, action.GET, self.device, self.port.id, slot))
        
    def latestValue(self):
        return self._value

    def latestValueAndTime(self):
        return self._value, self._millis
    
    @abstractmethod
    def parseData(self, data):
        return None

    @abstractmethod
    def parseMillis(self, data):
        return None

class lightSensor(simpledevice, readabledevice):

    def __init__(self):
        simpledevice.__init__(self, device.LIGHT_SENSOR)
        readabledevice.__init__(self)
        
    def parseData(self, data):
        if len(data) != 4:
            raise PacketError("Expected 4 bytes of data returned. Got: " + str(len(data)))
        self._value = self.bytesToFloat(data, 0)

    def parseMillis(self, millis):
        if len(millis) != 4:
            print("Expected 4 bytes of data returned. Got: " + str(len(millis)))
           # raise PacketError("Expected 4 bytes of time returned. Got: " + str(len(data)))
        else:
            self._millis = self.bytesToFloat(millis, 0)

class lightAndGrayscaleSensor(simpledevice, readabledevice):

    def __init__(self):
        simpledevice.__init__(self, device.LIGHT_SENSOR)
        readabledevice.__init__(self)
        
    def lightOn(self):
        self.port.sendRequest(requestpacket(self.index, action.RUN, self.device, self.port.id, data=[1]))

    def lightOff(self):
        self.port.sendRequest(requestpacket(self.index, action.RUN, self.device, self.port.id, data=[0]))
        
    def parseData(self, data):
        if len(data) != 4:
            raise PacketError("Expected 4 bytes of data returned. Got: " + str(len(data)))
        self._value = self.bytesToFloat(data, 0)

    def parseMillis(self, millis):
        if len(millis) != 4:
            print("Expected 4 bytes of data returned. Got: " + str(len(millis)))
           # raise PacketError("Expected 4 bytes of time returned. Got: " + str(len(data)))
        else:
            self._millis = self.bytesToFloat(millis, 0)


class lineFollower(simpledevice, readabledevice):

    def __init__(self):
        simpledevice.__init__(self, device.LINEFOLLOWER)
        readabledevice.__init__(self)

    def parseData(self, data):
        if len(data) != 4:
            raise PacketError("Expected 4 bytes of data returned. Got: " + str(len(data)))
        self._value = self.bytesToFloat(data, 0)

    def parseMillis(self, millis):
        if len(millis) != 4:
            print("Expected 4 bytes of data returned. Got: " + str(len(millis)))
           # raise PacketError("Expected 4 bytes of time returned. Got: " + str(len(data)))
        else:
            self._millis = self.bytesToFloat(millis, 0)


class pirMotionSensor(simpledevice, readabledevice):

    MOTION_MODE_RETRIGGERABLE = 1
    MOTION_MODE_UNREPEATABLE = 0

    def __init__(self):
        simpledevice.__init__(self, device.PIRMOTION)
        readabledevice.__init__(self)
        
    def setModeToRetriggerable(self):
        self.port.sendRequest(requestpacket(self.index, action.RUN, self.device, self.port.id, data=[pirMotionSensor.MOTION_MODE_RETRIGGERABLE]))

    def setModeToUnrepeatable(self):
        self.port.sendRequest(requestpacket(self.index, action.RUN, self.device, self.port.id, data=[pirMotionSensor.MOTION_MODE_UNREPEATABLE]))
        
    def parseData(self, data):
        if len(data) != 1:
            raise PacketError("Expected 1 bytes of data returned. Got: " + str(len(data)))
        self._value = self.bytesToBool(data, 0)

    def parseMillis(self, millis):
        if len(millis) != 4:
            print("Expected 4 bytes of data returned. Got: " + str(len(millis)))
           # raise PacketError("Expected 4 bytes of time returned. Got: " + str(len(data)))
        else:
            self._millis = self.bytesToFloat(millis, 0)


class potentiometer(simpledevice, readabledevice):

    def __init__(self):
        simpledevice.__init__(self, device.POTENTIONMETER)
        readabledevice.__init__(self)

    def parseData(self, data):
        if len(data) != 4:
            raise PacketError("Expected 4 bytes of data returned. Got: " + str(len(data)))
        self._value = self.bytesToFloat(data, 0)

    def parseMillis(self, millis):
        if len(millis) != 4:
            print("Expected 4 bytes of data returned. Got: " + str(len(millis)))
           # raise PacketError("Expected 4 bytes of time returned. Got: " + str(len(data)))
        else:
            self._millis = self.bytesToFloat(millis, 0)


class sevenSegmentDisplay(simpledevice):

    def __init__(self):
        super(sevenSegmentDisplay, self).__init__(device.SEVSEG)
      
    def setValue(self, fl):
        self.port.sendRequest(requestpacket(self.index, action.RUN, self.device, self.port.id, data= struct.pack("1f",fl)))

    def parseData(self, data):
        raise PacketError("7 segment display should never receive data")

class temperatureSensor(slotteddevice, readabledevice):

    def __init__(self, moduleSlot):
        slotteddevice.__init__(self, device.TEMPERATURE_SENSOR, moduleSlot)
        readabledevice.__init__(self)

    def parseData(self, data):
        if len(data) != 4:
            raise PacketError("Expected 4 bytes of data returned. Got: " + str(len(data)))
        self._value = self.bytesToFloat(data, 0)

    def parseMillis(self, millis):
        if len(millis) != 4:
            print("Expected 4 bytes of data returned. Got: " + str(len(millis)))
           # raise PacketError("Expected 4 bytes of time returned. Got: " + str(len(data)))
        else:
            self._millis = self.bytesToFloat(millis, 0)


class soundSensor(simpledevice, readabledevice):

    def __init__(self):
        simpledevice.__init__(self, device.SOUND_SENSOR)
        readabledevice.__init__(self)

    def parseData(self, data):
        if len(data) != 4:
            raise PacketError("Expected 4 bytes of data returned. Got: " + str(len(data)))
        self._value = self.bytesToFloat(data, 0)

    def parseMillis(self, millis):
        if len(millis) != 4:
            print("Expected 4 bytes of data returned. Got: " + str(len(millis)))
           # raise PacketError("Expected 4 bytes of time returned. Got: " + str(len(data)))
        else:
            self._millis = self.bytesToFloat(millis, 0)


class leftUltrasonicSensor(simpledevice, readabledevice):

    def __init__(self):
        simpledevice.__init__(self, device.ULTRASONIC_SENSOR)
        readabledevice.__init__(self)

    def parseData(self, data):
        if len(data) != 4:
            print("Expected 4 bytes of data returned. Got: " + str(len(data)))
           # raise PacketError("Expected 4 bytes of data returned. Got: " + str(len(data)))
        else:
            self._value = self.bytesToFloat(data, 0)

    def parseMillis(self, millis):
        if len(millis) != 4:
            print("Expected 4 bytes of data returned. Got: " + str(len(millis)))
           # raise PacketError("Expected 4 bytes of time returned. Got: " + str(len(data)))
        else:
            self._millis = self.bytesToFloat(millis, 0)

class centerUltrasonicSensor(simpledevice, readabledevice):

    def __init__(self):
        simpledevice.__init__(self, device.ULTRASONIC_SENSOR)
        readabledevice.__init__(self)

    def parseData(self, data):
        if len(data) != 4:
            print("Expected 4 bytes of data returned. Got: " + str(len(data)))
           # raise PacketError("Expected 4 bytes of data returned. Got: " + str(len(data)))
        else:
            self._value = self.bytesToFloat(data, 0)

    def parseMillis(self, millis):
        if len(millis) != 4:
            print("Expected 4 bytes of data returned. Got: " + str(len(millis)))
           # raise PacketError("Expected 4 bytes of time returned. Got: " + str(len(data)))
        else:
            self._millis = self.bytesToFloat(millis, 0)



class rightUltrasonicSensor(simpledevice, readabledevice):

    def __init__(self):
        simpledevice.__init__(self, device.ULTRASONIC_SENSOR)
        readabledevice.__init__(self)

    def parseData(self, data):
        if len(data) != 4:
            print("Expected 4 bytes of data returned. Got: " + str(len(data)))
           # raise PacketError("Expected 4 bytes of data returned. Got: " + str(len(data)))
        else:
            self._value = self.bytesToFloat(data, 0)

    def parseMillis(self, millis):
        if len(millis) != 4:
            print("Expected 4 bytes of data returned. Got: " + str(len(millis)))
           # raise PacketError("Expected 4 bytes of time returned. Got: " + str(len(data)))
        else:
            self._millis = self.bytesToFloat(millis, 0)

class dcmotor(simpledevice):

    def __init__(self):
        simpledevice.__init__(self, device.MOTOR)


    def run(self, speed):
        self.port.sendRequest(requestpacket(self.index, action.RUN, self.device, self.port.id, data= struct.pack("1h",speed)))

    def stop(self):
        self.port.sendRequest(requestpacket(self.index, action.RUN, self.device, self.port.id, data= struct.pack("1h",0)))

    def parseData(self, data):
        return False

    def parseMillis(self, data):
        return False

# orion_firmware.ino uses the MeEncoderMotor() class which assumes the motor encoder board 
# is loaded with the old motor encoder firmware.    
#    1. void MeEncoderMotor::begin();
#    2. boolean MeEncoderMotor::reset();
#    3. boolean MeEncoderMotor::move(float angle, float speed);
#    4. boolean MeEncoderMotor::moveTo(float angle, float speed);
#    5. boolean MeEncoderMotor::runTurns(float turns, float speed);
#    6. boolean MeEncoderMotor::runSpeed(float speed);
#    7. boolean MeEncoderMotor::runSpeedAndTime(float speed, float time);
#    8. float MeEncoderMotor::getCurrentSpeed();
#    9. float MeEncoderMotor::getCurrentPosition();
# Currently it only supports the move() function.   
#   we'll implement run() and stop() via move() first, then add other functionality
#   from this older motor encoder firmware.  Getting current speed and position 
#   may prove quite useful if they actually work.    
#  Much more functionality is supported in the newer firmware.  
#   Note that Auriga and MegaPi .inos use the newer motor encoder firmware and motor encoder libraries. 

class encodermotor(slotteddevice):

    def __init__(self, moduleslot):
       slotteddevice.__init__(self, device.ENCODER, moduleslot)  # we'll start as a slotteddevice;  no data expected back
       

# Port1, slot 1, speed 128, distance 0  -  Motor 1 moves continuously atr speed of 128
# preamble  len  idx  action (GET)  device (12)  port  slot speed  distance (angle)
# ff 55     0b   00   02            0c           08    01   80 00  00 00 00 00
#  the device is 12, the encoder
#  the port is always the same (0x08 == 9) as it refers to the i2c slave address of the motor encoder board
#  the slot is the motor;  there are two connected to the board
#  speed is a short (16-bit signed int) that has the least significant byte first
#  distance is in degrees and is a float (4-bytes)  with the lsb first. 

# the encoder motor 
    def run(self, speed):
        self.port.sendRequest(
            requestpacket(self.index, action.RUN, self.device, 
                          0x08,    # always refers to i2c address of motor encoder board; self.port.id, 
                          self.slot,
                          data= struct.pack("1h1f",speed,0.0)))  # run the requested speed forever

#  Port1, slot 1, speed 0, distance 0  -  no motion on any motor (value sent to motor 1, the right motor)
#  ff 55 0b 00 02 0c 08 01 00 00 00 00 00 00

    def stop(self):
        self.port.sendRequest(
            requestpacket(self.index, action.RUN, self.device, 
                          0x08,  # self.port.id, 
                          self.slot,
                          data= struct.pack("1h1f",0, 0.0)))

    def parseData(self, data):
        return False

    def parseMillis(self, data):
        return False