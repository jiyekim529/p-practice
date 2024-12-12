class CarControl:
    """Controls the movement of the car by managing motor speeds and directions."""

    def __init__(self, car):
        """
        Initializes the CarControl instance with a car object.

        Args:
            car: An instance of the car class that provides methods to control the car's movement.
        """
        self.car                   = car
        self.motor_up_speed        = 68
        self.motor_corner_speed    = 58
        self.motor_down_speed      = 55
        self.left_reduced_speed    = 40
        self.right_increased_speed = 85

    def control(self, direction):
        """
        Controls the car's movement based on the specified direction.

        Args:
            direction (str): The direction command to control the car.
                             Possible values: "REDUCED_LEFT", "REDUCED_RIGHT", "UP", "LEFT", "RIGHT".
        """
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

    def stop(self):
        """
        Stops the car by calling the Car_Stop method of the car object.
        """
        self.car.Car_Stop()