import cv2
import numpy as np
import time

from YB_Pcb_Car import YB_Pcb_Car
from camera import Camera
from car_control import CarControl
from image_processor import ImageProcessor
from cascade_loader import CascadeLoader
from buzzer import Buzzer
from servo_motor import ServoMotor


class Manager:
    def __init__(self):
        self.camera          = Camera()
        self.car             = YB_Pcb_Car.YB_Pcb_Car()
        self.car_control     = CarControl(self.car)
        self.image_processor = ImageProcessor()
        self.buzzer          = Buzzer()
        self.servo_motor     = ServoMotor(self.camera.cap)

        # 캐스케이드 분류기 로드
        self.cascades = {
            'B_Total': CascadeLoader.load_cascade('data/signer_b_total.xml'),
            '0_Total': CascadeLoader.load_cascade('data/signer_o_t_total.xml'),
            'T_Total': CascadeLoader.load_cascade('data/signer_t_t_total.xml'),
            'O_Total': CascadeLoader.load_cascade('data/O_total.xml')
        }

        self.last_o_time = None  # 마지막 'O_Total' 감지 시간

    def handle_detection(self, detection):
        # T_Total이나 0_Total을 감지한 경우 3번 경고음 발생시키고 O_Total을 감지했다면 프로그램 종료
        actions = {
            'T_Total': lambda: self._stop_action("same", 3),
            '0_Total': lambda: self._stop_action("diff", 3),
            'O_Total': self._exit_program,
        }

        action = actions.get(detection)
        if action: action()

    def _stop_action(self, beep_type, count):
        time.sleep(2) # 2초 대기
        self.buzzer.beep(beep_type, count)
        time.sleep(1)

    def _exit_program(self):
        self.car.Car_Run(80, 80)
        self.car_control.stop()
        print("Detected 'O_Total'. Parking and exiting the program.")
        exit()

    def run(self):
        try:
            while True:
                frame = self.camera.capture_frame() # 프레임 캡처
                if frame is None: continue # 프레임 캡처 실패 시 다음 프레임으로 넘어감

                processed_frame = self.image_processor.process_frame(frame) # 프레임 전처리
                histogram       = np.sum(processed_frame, axis=0)   # 히스토그램 생성
                direction       = self.image_processor.decide_direction(histogram) # 방향 결정

                # B_Total, 0_Total, T_Total, O_Total 감지
                detections = {
                    'B_Total': self.image_processor.detect_symbol(frame, self.cascades['B_Total']),
                    '0_Total': self.image_processor.detect_symbol(frame, self.cascades['0_Total']),
                    'T_Total': self.image_processor.detect_symbol(frame, self.cascades['T_Total']),
                    'O_Total': self.image_processor.detect_symbol(frame, self.cascades['O_Total'])
                }

                # B_Total, 0_Total, T_Total, O_Total 중 하나라도 감지되면 해당 동작 수행    
                for detection, detected in detections.items():
                    if detected:
                        self.handle_detection(detection)
                        break
                else:
                    # 검정 바닥이 감지되지 않은 경우 서보모터를 이용해 좌우로 움직이며 탐색
                    if self.image_processor.detect_non_black(frame):
                        result = self.servo_motor.rotate_and_detect(self.car, self.image_processor)
                        if result:
                            self.handle_detection(result)
                        else: 
                            # 서보모니터 탐색 결과가 없는 경우 후진 후 다시 탐색
                            self.car_control.control("BACK")
                            time.sleep(1.5)
                            result = self.servo_motor.rotate_and_detect(self.car, self.image_processor)
                            if result:
                                self.handle_detection(result)
                            else: 
                                # 후진 후 탐색 결과가 없는 경우 다시 전진
                                self.car_control("RUN")
                                if direction in ["UP", "LEFT", "RIGHT"]:
                                    self.car_control.control(direction)
                    else:
                        # 검정 바닥이 감지된 경우 방향 결정 
                        if direction in ["UP", "LEFT", "RIGHT"]:
                            # UP, LEFT, RIGHT 중 하나인 경우 해당 방향으로 이동
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

if __name__ == "__main__":
    manager = Manager()
    manager.run()