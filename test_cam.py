import cv2
import time

def test_opencv_camera():
    # Attempt to open camera using index 0
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    
    if not cap.isOpened():
        print("ERROR: Could not open camera (Index 0 failed).")
        print("Suggestion: Check config.txt for dtoverlay=ov5647 and reboot, or enable Legacy Camera in raspi-config.")
        return

    # Set resolution for testing
    width, height = 320, 240
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    print("Camera opened successfully.")
    
    # Capture 5 frames to warm up and test capture ability
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"Frame {i+1} captured. Resolution: {frame.shape}")
        else:
            print(f"ERROR: Failed to capture frame {i+1}.")
            cap.release()
            return
    
    # Save the last frame for visual confirmation
    output_filename = "test_image.jpg"
    cv2.imwrite(output_filename, frame)
    print(f"Successfully saved test image to {output_filename}")

    # Release resources
    cap.release()
    print("Camera released.")

if __name__ == "__main__":
    # Ensure you are running within the virtual environment: source venv/bin/activate
    test_opencv_camera()
