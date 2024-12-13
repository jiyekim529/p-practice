import time

class ServoMotor:
    def __init__(self, cap):
        self.cap = cap
        self.servo_angle = 30 # 초기 앵글 각도

    def move_servo(self, car, angle):
        self.servo_angle = angle
        car.Ctrl_Servo(1, self.servo_angle)
        car.Ctrl_Servo(2, self.servo_angle)
        time.sleep(0.5)

    def rotate_and_detect(self, car, detection, cascades):
        attempts     = 0
        max_attempts = 5

        self.move_servo(car, 30) 
        
        angles = [15, 30, 45, 30] # 좌우로 움직일 각도

        while attempts < max_attempts:
            for angle in angles:
                self.move_servo(car, angle)
                ret, frame = self.cap.read()
                if not ret: continue

                # ImageProcessor 클래스에서 detection 결과를 받아옴
                if detection.detect_symbol(frame, cascades['O_Total']): return 'O_Total'
                elif detection.detect_symbol(frame, cascades['B_Total']):break
                else:
                    attempts += 1
                    continue  # 내부 for 루프가 break 없이 완료되면 다음 시도

            # B_Total을 감지한 경우 고개를 들어 추가 탐색
            self.move_servo(car, 60)  # 고개를 들어 위를 봄
            time.sleep(1)
            ret, frame = self.cap.read()
            if not ret: continue
            if detection.detect_symbol(frame, cascades['T_Total']): return "T_Total"
            elif detection.detect_symbol(frame, cascades['0_Total']): return "0_Total"

            attempts += 1

        return None