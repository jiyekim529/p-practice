import RPi.GPIO as GPIO
import time

class Buzzer:
    """Controls a buzzer connected to a Raspberry Pi GPIO pin."""

    def __init__(self, pin=27):
        """
        Initializes the Buzzer instance.

        Args:
            pin (int): GPIO pin number where the buzzer is connected. Default is 27.
        """
        self.pin = pin  # GPIO pin number connected to the buzzer
        self.setup()

    def setup(self):
        """Configures the GPIO settings for the buzzer."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def buzz(self, frequency, duration):
        """
        Generates a buzz sound at a specified frequency and duration.

        Args:
            frequency (int) : Frequency of the buzz in Hertz. If set to 0, the buzzer remains silent.
            duration (float): Duration of the buzz in seconds.
        """
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
        """
        Plays a beep pattern based on the specified tone type.

        Args:
            tone_type (str): Type of beep pattern ('same' or 'diff').
            times (int): Number of times the beep pattern is repeated. Default is 3.
            duration (float): Duration of each beep in seconds. Default is 0.2.
        """
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

    def destroy(self):
        """Cleans up the GPIO settings."""
        GPIO.cleanup()