class CarControl:
    def __init__(self, car):
        self.car                   = car
        self.motor_up_speed        = 68
        self.motor_corner_speed    = 58
        self.motor_down_speed      = 55
        self.left_reduced_speed    = 40
        self.right_increased_speed = 85

    def control(self, direction):
        if direction == "REDUCED_LEFT":
            self.car.Car_Run(self.left_reduced_speed, self.right_increased_speed)
        elif direction == "REDUCED_RIGHT":
            self.car.Car_Run(self.right_increased_speed, self.left_reduced_speed)
        elif direction == "UP":
            self.car.Car_Run(self.motor_up_speed, self.motor_up_speed)
        elif direction == "LEFT":
            self.car.Car_Left(self.motor_down_speed, self.motor_corner_speed)
        elif direction == "RIGHT":
            self.car.Car_Right(self.motor_corner_speed, self.motor_down_speed)
        elif direction == "BACK":
            self.car.Car_Back(self.motor_down_speed, self.motor_down_speed)
        elif direction == "RUN":
            self.car.Car_Run(self.motor_up_speed, self.motor_up_speed)

    def stop(self):
        self.car.Car_Stop()