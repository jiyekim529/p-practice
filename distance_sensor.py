import RPi.GPIO as GPIO
import time

class DistanceSensor:
    def __init__(self, trig_pin, echo_pin):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def get_distance(self):
        # 초음파 트리거 신호
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)

        start_time = time.time()
        stop_time = time.time()

        # Echo 핀 High 신호까지 대기
        while GPIO.input(self.echo_pin) == 0: start_time = time.time()

        # Echo 핀 Low 복귀까지 대기
        while GPIO.input(self.echo_pin) == 1: stop_time = time.time()

        # 시간 차로 거리 계산
        time_elapsed = stop_time - start_time
        distance = (time_elapsed * 34300) / 2  # 음속 34300cm/s
        return distance