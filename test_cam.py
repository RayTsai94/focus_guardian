import cv2
import time
import numpy as np
from picamera2 import Picamera2

def test_opencv_camera_picamera2():
    print("--- Picamera2 Camera Test Started ---")
    
    width, height = 320, 240

    try:
        # 1. Initialize Picamera2
        picam2 = Picamera2()
        
        # 2. Configure for video (low resolution for speed)
        config = picam2.create_video_configuration(main={"size": (width, height), "format": "RGB888"})
        picam2.configure(config)
        
        # 3. Start the stream
        picam2.start()
        print("Camera stream successfully started.")
        
        time.sleep(1.0) # Wait for auto-exposure to settle

        # 4. Capture 5 frames to test capture ability
        for i in range(5):
            # Capture frame directly into a NumPy array
            frame_rgb = picam2.capture_array()
            
            # Convert RGB array to OpenCV's preferred BGR format
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            print(f"Frame {i+1} captured. Resolution: {frame_bgr.shape}")
        
        # 5. Save the last frame for visual confirmation
        output_filename = "test_image_picamera2.jpg"
        cv2.imwrite(output_filename, frame_bgr)
        print(f"SUCCESS: Saved test image to {output_filename}")

    except Exception as e:
        print(f"FAILURE: An error occurred during camera operation: {e}")
        print("Suggestion: Ensure all Picamera2 dependencies are installed (e.g., sudo apt install python3-picamera2).")

    finally:
        # 6. Release resources
        if 'picam2' in locals() and picam2.started:
            picam2.stop()
            print("Camera stream released.")

if __name__ == "__main__":
    test_opencv_camera_picamera2()
