import time
from PCA9685 import PCA9685

class PanTiltController:
    def __init__(self):
        try:
            self.pwm = PCA9685(0x40, debug=False)
            self.pwm.setPWMFreq(50)
            self.PAN_CHANNEL = 0
            self.TILT_CHANNEL = 1
            self.current_pan = 90
            self.current_tilt = 90
            self.center()
        except Exception as e:
            print(f"Warning: motor_contorl fails to initialize({e}), please check if I2C is functioning")

    def set_angle(self, channel, angle):
        if angle < 0: angle = 0
        if angle > 180: angle = 180
        try:
            self.pwm.setRotationAngle(channel, angle)
        except:
            pass
        return angle

    def pan(self, angle):
        self.current_pan = self.set_angle(self.PAN_CHANNEL, angle)

    def tilt(self, angle):
        self.current_tilt = self.set_angle(self.TILT_CHANNEL, angle)
        
    def center(self):
        self.pan(90)
        self.tilt(90)
        time.sleep(0.5)