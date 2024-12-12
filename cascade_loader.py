import os
import cv2

class CascadeLoader:
    """Utility class for loading OpenCV Cascade Classifiers."""

    @staticmethod
    def load_cascade(file_path):
        """
        Loads a Cascade Classifier from the specified file path.

        Args:
            file_path (str): The path to the cascade XML file.

        Returns:
            cv2.CascadeClassifier: The loaded Cascade Classifier. Returns an empty classifier if loading fails.
        """
        if os.path.exists(file_path):
            cascade = cv2.CascadeClassifier(file_path)
            if cascade.empty():
                print(f"Error loading cascade from {file_path} - Cascade is empty.")
            else:
                print(f"Successfully loaded cascade from {file_path}.")
            return cascade
        else:
            print(f"File not found: {file_path}")
            return cv2.CascadeClassifier()