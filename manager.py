import cv2
import numpy as np
import time
import RPi.GPIO as GPIO

from new_self_driving_car import YB_Pcb_Car
from camera import Camera
from car_control import CarControl
from image_processor import ImageProcessor
from cascade_loader import CascadeLoader
from buzzer import Buzzer
from servo_motor import ServoMotor
from distance_sensor import DistanceSensor


class Manager:
    """Manages the autonomous driving system by handling camera input, image processing, car control, and event detections."""

    def __init__(self):
        """
        Initializes the Manager with necessary components and loads cascade classifiers.
        
        This includes initializing the camera, car, car controller, image processor, and buzzer.
        Additionally, it loads various cascade classifiers for symbol detection.
        """
        GPIO.setmode(GPIO.BCM)
        self.camera          = Camera()
        self.car             = YB_Pcb_Car.YB_Pcb_Car()
        self.car_control     = CarControl(self.car)
        self.image_processor = ImageProcessor()
        self.buzzer          = Buzzer()
        self.last_o_time     = None  # Records the last time 'O_Total' was detected
        self.sign_check_mode = False # Mode for checking signs after detecting ground symbols
        self.servo           = ServoMotor(pan_pin=, tilt_pin=)
        self.distance_sensor = DistanceSensor(trig_pin=, echo_pin=)

        # Load Cascade Classifiers
        self.cascades = {
            'X': CascadeLoader.load_cascade('data/cascade_x.xml'),
            'B_Right': CascadeLoader.load_cascade('data/signer_b_right.xml'),
            'B_Left': CascadeLoader.load_cascade('data/signer_b_t_left.xml'),
            'B_Total': CascadeLoader.load_cascade('data/signer_b_total.xml'),
            # '0_right': CascadeLoader.load_cascade('data/signer_o_t_right.xml'),
            '0_left': CascadeLoader.load_cascade('data/signer_o_t_left.xml'),
            '0_total': CascadeLoader.load_cascade('data/singer_0_t_total.xml'),
            'T_right': CascadeLoader.load_cascade('data/signer_t_t_right.xml'),
            'T_left': CascadeLoader.load_cascade('data//signer_t_t_left.xml'),
            'T_total': CascadeLoader.load_cascade('data//signer_t_t_total.xml'),
            'O_Left': CascadeLoader.load_cascade('data/O_left.xml'),
            'O_Right': CascadeLoader.load_cascade('data/O_right.xml'),
            'O_Total': CascadeLoader.load_cascade('data/O_total.xml')
        }

    def handle_detection(self, detection):
        """
        Executes actions based on the detected symbol.
        
        Args:
            detection (str): The type of symbol detected.
        """
        if detection.startswith('b_'):
            self.sign_check_mode = True # Switch to sign analysis mode
            return 

        if self.sign_check_mode:
            if detection.startswith('t_'):
                self._stop_action("same", 3)
                self.sign_check_mode = False
            elif detection.startswith('0_'):
                self._stop_action("diff", 3)
                self.sign_check_mode = False
            return

        if detection == 'X':
            self._turn_action("RIGHT", "Detected 'X'. Turning right.")
        elif detection == 'O_Total':
            self._exit_program()
        elif detection == 'O_Left':
            self._turn_action("LEFT", "Detected 'O_Left'. Turning left.")
        elif detection == 'O_Right':
            self._turn_action("RIGHT", "Detected 'O_Right'. Turning right.")

    def _stop_action(self, beep_type, count):
        """
        Stops the car and triggers a buzzer beep.
        
        Args:
            beep_type (str): Type of beep pattern ('same' or 'diff').
            count (int): Number of beep repetitions.
        """
        self.car_control.stop()
        self.buzzer.beep(beep_type, count)
        time.sleep(1)

    def _turn_action(self, direction, message):
        """
        Turns the car in the specified direction and logs a message.
        
        Args:
            direction (str): Direction to turn ('LEFT' or 'RIGHT').
            message (str): Message to log regarding the action.
        """
        print(message)
        self.car_control.control(direction)
        time.sleep(1)

    def _exit_program(self):
        """
        Stops the car and exits the program gracefully.
        """
        self.car_control.stop()
        print("Detected 'O_Total'. Parking and exiting the program.")
        exit()

    def scan_with_servo(self):
        # 상, 하, 좌, 우, 중간 각도로 서보를 움직이며 스캔
        angles = [
            (90, 90),   # 중앙
            (60, 90),   # 왼쪽
            (120, 90),  # 오른쪽
            (90, 60),   # 위
            (90, 120)   # 아래
        ]
        for pan_angle, tilt_angle in angles:
            self.servo.set_pan_angle(pan_angle)
            self.servo.set_tilt_angle(tilt_angle)
            time.sleep(0.2)
            frame = self.camera.capture_frame()
            if frame is None:
                continue
            yield frame

    def cleanup(self):
        self.car_control.stop()
        self.camera.release()
        self.servo.cleanup()
        cv2.destroyAllWindows()
        GPIO.cleanup()

    def run(self):
        try:
            while True:
                # 초음파 거리 측정
                dist = self.distance_sensor.get_distance()
                print(f"Distance: {dist:.2f} cm")

                # 너무 가까우면 정지
                if dist < 20:
                    self.car_control.stop()
                    print("Obstacle too close! Stopping.")
                    time.sleep(1)
                    continue

                # 서보로 카메라 방향 전환하며 탐색
                for frame in self.scan_with_servo():
                    processed_frame = self.image_processor.process_frame(frame)
                    histogram = np.sum(processed_frame, axis=0)
                    direction = self.image_processor.decide_direction(histogram)

                    # 각 cascade로 기호 검출
                    detections = {
                        '0_total': self.image_processor.detect_symbol(frame, self.cascades['0_total']),
                        '0_left': self.image_processor.detect_symbol(frame, self.cascades['0_left']),
                        '0_right': self.image_processor.detect_symbol(frame, self.cascades['0_right']),
                        't_total': self.image_processor.detect_symbol(frame, self.cascades['T_total']),
                        't_left': self.image_processor.detect_symbol(frame, self.cascades['T_left']),
                        't_right': self.image_processor.detect_symbol(frame, self.cascades['T_right']),
                        'b_total': self.image_processor.detect_symbol(frame, self.cascades['B_Total']),
                        'b_left': self.image_processor.detect_symbol(frame, self.cascades['B_Left']),
                        'b_right': self.image_processor.detect_symbol(frame, self.cascades['B_Right']),
                        'X': self.image_processor.detect_symbol(frame, self.cascades['X']),
                        'O_Left': self.image_processor.detect_symbol(frame, self.cascades['O_Left']),
                        'O_Right': self.image_processor.detect_symbol(frame, self.cascades['O_Right']),
                        'O_Total': self.image_processor.detect_symbol(frame, self.cascades['O_Total'])
                    }

                    detected_any = False
                    for detection, detected in detections.items():
                        if detected:
                            self.handle_detection(detection)
                            detected_any = True
                            break

                    if not detected_any:
                        if self.sign_check_mode:
                            self.car_control.control("UP")
                        else:
                            if direction in ["UP", "LEFT", "RIGHT"]:
                                self.car_control.control(direction)
                            else:
                                self.car_control.stop()

                    cv2.imshow('Processed Frame', processed_frame)
                    key = cv2.waitKey(30) & 0xff
                    if key == 27:  # ESC
                        return
                    elif key == 32: # SPACE
                        print("Paused for debugging. Press any key to continue.")
                        cv2.waitKey()

        except Exception as e:
            print(f"Error occurred: {e}")

        finally:
            self.cleanup()

if __name__ == "__main__":
    manager = Manager()
    manager.run()