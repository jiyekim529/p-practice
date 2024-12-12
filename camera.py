import cv2

class Camera:
    """Handles camera operations using OpenCV."""

    def __init__(self):
        """
        Initializes the Camera instance and sets up the camera parameters.
        """
        self.cap = cv2.VideoCapture(0)  # Initialize the default camera
        self.setup()

    def setup(self):
        """
        Configures the camera settings such as resolution, brightness, contrast, saturation, and gain.
        """
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   # Set frame width to 320 pixels
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # Set frame height to 240 pixels
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 20)     # Set brightness level
        self.cap.set(cv2.CAP_PROP_CONTRAST, 100)      # Set contrast level
        self.cap.set(cv2.CAP_PROP_SATURATION, 30)     # Set saturation level
        self.cap.set(cv2.CAP_PROP_GAIN, 20)           # Set gain level

    def capture_frame(self):
        """
        Captures a single frame from the camera.

        Returns:
            frame (numpy.ndarray): The captured frame image. Returns None if the frame capture fails.
        """
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to read frame from camera.")
            return None
        return frame

    def release(self):
        """
        Releases the camera resource.
        """
        self.cap.release()