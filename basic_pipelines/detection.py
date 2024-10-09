import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
import cv2
import hailo
from hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
from detection_pipeline import GStreamerDetectionApp

# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
# Inheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.new_variable = 42  # New variable example

    def new_function(self):  # New function example
        return "The meaning of life is: "

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------

# This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):
    print("Ma : app_callback1")
    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    print("Ma : app_callback2")
    # Check if the buffer is valid
    if buffer is None:
        return Gst.PadProbeReturn.OK
    print("Ma : app_callback3")
    # Using the user_data to count the number of frames
    user_data.increment()
    print("Ma : app_callback4")
    string_to_print = f"Frame count: {user_data.get_count()}\n"
    print("Ma : app_callback5")
    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)
    print("Ma : app_callback6")
    # If the user_data.use_frame is set to True, we can get the video frame from the buffer
    frame = None
    print("Ma : app_callback7")
    if user_data.use_frame and format is not None and width is not None and height is not None:
        # Get video frame
        frame = get_numpy_from_buffer(buffer, format, width, height)
    print("Ma : app_callback8")
    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    print("Ma : app_callback9")
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)
    print("Ma : app_callback10")
    # Parse the detections
    detection_count = 0
    print("Ma : app_callback11")
    for detection in detections:
        label = detection.get_label()
        bbox = detection.get_bbox()
        confidence = detection.get_confidence()
        if label == "person":
            string_to_print += f"Detection: {label} {confidence:.2f}\n"
            detection_count += 1
    print("Ma : app_callback12")        
    if user_data.use_frame:
        # Note: using imshow will not work here, as the callback function is not running in the main thread
        # Let's print the detection count to the frame
        cv2.putText(frame, f"Detections: {detection_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # Example of how to use the new_variable and new_function from the user_data
        # Let's print the new_variable and the result of the new_function to the frame
        cv2.putText(frame, f"{user_data.new_function()} {user_data.new_variable}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # Convert the frame to BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        user_data.set_frame(frame)
    print("Ma : app_callback12")         

    print(string_to_print)
    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    # Create an instance of the user app callback class
    user_data = user_app_callback_class()
    app = GStreamerDetectionApp(app_callback, user_data)
    app.run()
