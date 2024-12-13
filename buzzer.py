import RPi.GPIO as GPIO
import time

class Buzzer:
    def __init__(self, pin=22):
        self.pin = pin
        self.setup()

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def buzz(self, frequency, duration):
        if frequency == 0:
            time.sleep(duration)
            return
        period      = 1.0 / frequency
        delay_value = period / 2
        cycles      = int(duration * frequency)
        for _ in range(cycles):
            GPIO.output(self.pin, True)
            time.sleep(delay_value)
            GPIO.output(self.pin, False)
            time.sleep(delay_value)

    def beep(self, tone_type, times=3, duration=0.2):
        if tone_type == "same":
            for _ in range(times):
                self.buzz(1000, duration)
                time.sleep(duration)
        elif tone_type == "diff":
            frequencies = [800, 1000, 1200]
            for i in range(times):
                freq = frequencies[i % len(frequencies)]
                self.buzz(freq, duration)
                time.sleep(0.1)
        else: pass

    def destroy(self): GPIO.cleanup()