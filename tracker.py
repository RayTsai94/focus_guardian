import cv2
import time
import threading
import numpy as np
from picamera2 import Picamera2
from motor_control import PanTiltController
from audio_manager import AudioManager 

class FocusTracker:
    def __init__(self):
        self.controller = PanTiltController()
        self.audio = AudioManager()
        self.is_running = False
        self.events_log = []
        
        #  PICAMERA2 SETUP
        try:
            self.picam2 = Picamera2()
            self.WIDTH, self.HEIGHT = 320, 240
            
            # Configure camera for low resolution and RGB output 
            config = self.picam2.create_video_configuration(main={"size": (self.WIDTH, self.HEIGHT), "format": "RGB888"})
            self.picam2.configure(config)
            print("Picamera2 configured successfully.")
        except Exception as e:
            print(f"FATAL ERROR: Picamera2 initialization failed: {e}")
            raise
        
        # PID Parameters
        self.Kp = 0.07
        self.dead_zone = 30
        
        # Zone Thresholds (90 is horizon)
        # >110 Looking up (Face = Violation)
        # <80 Looking down (Desk = Safe)
        self.SAFE_TILT = 80
        self.FORBIDDEN_TILT = 110
        self.last_zone = "SAFE"

    def start_tracking(self, duration_minutes):
        if self.is_running: return
        self.is_running = True
        self.events_log = [] # Clear logs
        self.audio.speak(f"Focus mode started for {duration_minutes} minutes", "start")
        threading.Thread(target=self._loop, args=(duration_minutes,)).start()

    def stop_tracking(self):
        self.is_running = False
        self.audio.speak("Focus mode ended", "stop")

    def get_logs(self):
        return self.events_log
    
    def _loop(self, duration_minutes):
        print("Starting Picamera2 tracking loop.")
        
        # 1. Start the camera stream
        self.picam2.start()
        time.sleep(1.0) # Warm up 

        # 2. Initial Frame Capture for CSRT Tracker
        frame_rgb = self.picam2.capture_array()
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
        # Initialize CSRT Tracker
        tracker = cv2.TrackerCSRT_create()
        center_x, center_y = self.WIDTH // 2, self.HEIGHT // 2
        bbox = (center_x - 30, center_y - 30, 60, 60)
        tracker.init(frame_bgr, bbox)
        
        end_time = time.time() + (duration_minutes * 60)

        while self.is_running and time.time() < end_time:
            
            # 3. Direct Frame Capture (Bypass V4L2)
            frame_rgb = self.picam2.capture_array() 
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR) # Convert for OpenCV
            
            success, bbox = tracker.update(frame)

            if success:
                x, y, w, h = [int(v) for v in bbox]
                obj_x = x + w // 2
                obj_y = y + h // 2
                
                # PID Control (unchanged logic)
                err_x = center_x - obj_x
                err_y = center_y - obj_y
                
                if abs(err_x) > self.dead_zone:
                    self.controller.current_pan += err_x * self.Kp
                    self.controller.pan(self.controller.current_pan)
                
                if abs(err_y) > self.dead_zone:
                    self.controller.current_tilt -= err_y * self.Kp
                    self.controller.tilt(self.controller.current_tilt)

                # Zone Logic 
                tilt = self.controller.current_tilt
                if tilt > self.FORBIDDEN_TILT:
                    if self.last_zone!= "FORBIDDEN":
                        print(">> Violation! Phone moved to face area.")
                        self.audio.speak("Please focus, do not look at your phone", "violation")
                        self.events_log.append({"type": "violation", "time": time.time()})
                        self.last_zone = "FORBIDDEN"
                elif tilt < self.SAFE_TILT:
                    if self.last_zone == "FORBIDDEN":
                        print(">> Back to focus.")
                        self.audio.speak("Good job, keep it up", "safe")
                        self.last_zone = "SAFE"
            
            time.sleep(0.03) # CPU yield

        # 4. Clean up
        self.picam2.stop()
        self.controller.center()
        self.is_running = False
