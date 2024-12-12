import cv2
import numpy as np

class ImageProcessor:
    """Processes images for autonomous vehicle navigation using computer vision techniques."""

    def __init__(self, detect_value=30, r_weight=33, g_weight=33, b_weight=33, y_value=10):
        """
        Initializes the ImageProcessor with specific detection and weighting parameters.

        Args:
            detect_value (int): Threshold value for binary image thresholding.
            r_weight (int): Weight for the red channel.
            g_weight (int): Weight for the green channel.
            b_weight (int): Weight for the blue channel.
            y_value (int): Vertical offset for perspective transformation.
        """
        total_weight      = r_weight + g_weight + b_weight
        self.detect_value = detect_value
        self.r_weight     = r_weight / total_weight  # Normalize red channel weight
        self.g_weight     = g_weight / total_weight  # Normalize green channel weight
        self.b_weight     = b_weight / total_weight  # Normalize blue channel weight
        self.y_value      = y_value

    def weight_gray(self, image):
        """
        Converts a BGR image to a weighted grayscale image based on predefined channel weights.

        Args:
            image (numpy.ndarray): The input BGR image.

        Returns:
            numpy.ndarray: The resulting weighted grayscale image.
        """
        return cv2.addWeighted(
            cv2.addWeighted(image[:, :, 2], self.r_weight, image[:, :, 1], self.g_weight, 0),
            1.0, image[:, :, 0], self.b_weight, 0)

    def process_frame(self, input_frame):
        """
        Processes an input frame by applying perspective transformation and thresholding.

        Args:
            input_frame (numpy.ndarray): The input BGR frame captured from the camera.

        Returns:
            numpy.ndarray: The binary frame after processing.
        """
        pts_src = np.float32([
            [10, 70 + self.y_value],
            [310, 70 + self.y_value],
            [310, 10 + self.y_value],
            [10, 10 + self.y_value]
        ])
        pts_dst = np.float32([
            [0, 240],
            [320, 240],
            [320, 0],
            [0, 0]
        ])

        pts         = pts_src.reshape((-1, 1, 2)).astype(np.int32)
        input_frame = cv2.polylines(input_frame, [pts], isClosed=True, color=(0, 0, 255), thickness=2)

        mat_affine        = cv2.getPerspectiveTransform(pts_src, pts_dst)
        frame_transformed = cv2.warpPerspective(input_frame, mat_affine, (320, 240))
        gray_frame        = self.weight_gray(frame_transformed)
        _, binary_frame   = cv2.threshold(gray_frame, self.detect_value, 255, cv2.THRESH_BINARY)

        return binary_frame

    def decide_direction(self, histogram, direction_threshold=264103, up_threshold=50000):
        """
        Determines the driving direction based on the total sum of the histogram.

        Args:
            histogram (numpy.ndarray): The sum of pixel values along the vertical axis.
            direction_threshold (int): Threshold to decide direction.
            up_threshold (int): Threshold to decide whether to move forward.

        Returns:
            str: The decided direction ("UP" or "RANDOM").
        """
        total = np.sum(histogram)
        print("total:", total)

        if total > direction_threshold: return "UP"
        else: return "RANDOM"

    def detect_symbol(self, frame, cascade):
        """
        Detects symbols in a frame using a specified Cascade Classifier.

        Args:
            frame (numpy.ndarray): The input BGR frame.
            cascade (cv2.CascadeClassifier): The trained Cascade Classifier for symbol detection.

        Returns:
            bool: True if any symbols are detected, False otherwise.
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        symbols    = cascade.detectMultiScale(
                        gray_frame,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30)
                    )
        for (x, y, w, h) in symbols:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return len(symbols) > 0
