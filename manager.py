import cv2
import numpy as np
import time

from new_self_driving_car import YB_Pcb_Car
from camera import Camera
from car_control import CarControl
from image_processor import ImageProcessor
from cascade_loader import CascadeLoader
from buzzer import Buzzer

class Manager:
    """Manages the autonomous driving system by handling camera input, image processing, car control, and event detections."""

    def __init__(self):
        """
        Initializes the Manager with necessary components and loads cascade classifiers.
        
        Initializes the camera, car, car controller, image processor, and buzzer.
        Loads various cascade classifiers for symbol detection.
        """
        self.camera          = Camera()
        self.car             = YB_Pcb_Car.YB_Pcb_Car()
        self.car_control     = CarControl(self.car)
        self.image_processor = ImageProcessor()
        self.buzzer          = Buzzer()

        # Load Cascade Classifiers
        self.cascades = {
            'X': CascadeLoader.load_cascade('data/cascade_x.xml'),
            'Threat': CascadeLoader.load_cascade('data/threat.xml'),
            'Stop': CascadeLoader.load_cascade('data/stop.xml'),
            'O_Left': CascadeLoader.load_cascade('data/O_left.xml'),
            'O_Right': CascadeLoader.load_cascade('data/O_right.xml'),
            'O_Total': CascadeLoader.load_cascade('data/O_total.xml')
        }

        self.last_o_time = None  # Records the last time 'O_Total' was detected

    def handle_detection(self, detection):
        """
        Executes actions based on the detected symbol.
        
        Args:
            detection (str): The type of symbol detected.
        """
        actions = {
            'Stop': lambda: self._stop_action("same", 3),
            'Threat': lambda: self._stop_action("diff", 3),
            'X': lambda: self._turn_action("RIGHT", "Detected 'X'. Turning right."),
            'O_Total': self._exit_program,
            'O_Left': lambda: self._turn_action("LEFT", "Detected 'O_Left'. Turning left."),
            'O_Right': lambda: self._turn_action("RIGHT", "Detected 'O_Right'. Turning right.")
        }

        action = actions.get(detection)
        if action: action()

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

    def run(self):
        """
        Starts the main loop to continuously process frames and handle detections.
        """
        try:
            while True:
                frame = self.camera.capture_frame()
                if frame is None: continue

                processed_frame = self.image_processor.process_frame(frame)
                histogram       = np.sum(processed_frame, axis=0)
                direction       = self.image_processor.decide_direction(histogram)

                # Detect symbols using Cascade Classifiers
                detections = {
                    'X': self.image_processor.detect_symbol(frame, self.cascades['X']),
                    'Threat': self.image_processor.detect_symbol(frame, self.cascades['Threat']),
                    'Stop': self.image_processor.detect_symbol(frame, self.cascades['Stop']),
                    'O_Left': self.image_processor.detect_symbol(frame, self.cascades['O_Left']),
                    'O_Right': self.image_processor.detect_symbol(frame, self.cascades['O_Right']),
                    'O_Total': self.image_processor.detect_symbol(frame, self.cascades['O_Total'])
                }

                for detection, detected in detections.items():
                    if detected:
                        self.handle_detection(detection)
                        break
                else:
                    # Follow the line based on the direction decision
                    if direction in ["UP", "LEFT", "RIGHT"]:
                        self.car_control.control(direction)
                    else: self.car_control.stop()

                cv2.imshow('Processed Frame', processed_frame)

                key = cv2.waitKey(30) & 0xff
                if key == 27: break
                elif key == 32:
                    print("Paused for debugging. Press any key to continue.")
                    cv2.waitKey()

        except Exception as e: print(f"Error occurred: {e}")

        finally:
            self.car_control.stop()
            self.camera.release()
            cv2.destroyAllWindows()