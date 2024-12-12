import RPi.GPIO as GPIO
import time

class ServoMotor:
    def __init__(self, pan_pin, tilt_pin, frequency=50):
        self.pan_pin    = pan_pin
        self.tilt_pin   = tilt_pin
        self.frequency  = frequency

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pan_pin, GPIO.OUT)
        GPIO.setup(self.tilt_pin, GPIO.OUT)

        self.pan_pwm  = GPIO.PWM(self.pan_pin, self.frequency)
        self.tilt_pwm = GPIO.PWM(self.tilt_pin, self.frequency)

        self.pan_pwm.start(0)
        self.tilt_pwm.start(0)

        # 초기 각도 설정
        self.set_pan_angle(90)
        self.set_tilt_angle(90)

    def set_pan_angle(self, angle):
        # 0도 ~ 180도 기준 -> 듀티비 변환
        duty = self.angle_to_duty(angle)
        self.pan_pwm.ChangeDutyCycle(duty)
        time.sleep(0.3)  # 모터가 움직일 시간
        self.pan_pwm.ChangeDutyCycle(0) # 서보 모터 떨림 감소를 위해 끔

    def set_tilt_angle(self, angle):
        duty = self.angle_to_duty(angle)
        self.tilt_pwm.ChangeDutyCycle(duty)
        time.sleep(0.3)
        self.tilt_pwm.ChangeDutyCycle(0)

    def angle_to_duty(self, angle): # 보정 필요 
        return 2 + (angle/180.0)*10

    def cleanup(self):
        self.pan_pwm.stop()
        self.tilt_pwm.stop()
        GPIO.cleanup([self.pan_pin, self.tilt_pin])