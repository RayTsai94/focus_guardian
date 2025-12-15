import cv2
import time
import threading
from motor_control import PanTiltController
from audio_manager import AudioManager

class FocusTracker:
    def __init__(self):
        self.controller = PanTiltController()
        self.audio = AudioManager()
        self.is_running = False
        self.events_log = []
        
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
        # On Bookworm, index 0 usually works. Try cv2.CAP_V4L2 if it fails.
        cap = cv2.VideoCapture(0)
        
        # Low resolution for performance
        width, height = 320, 240
        cap.set(3, width)
        cap.set(4, height)
        center_x, center_y = width // 2, height // 2

        tracker = cv2.TrackerCSRT_create()
        
        # Warm up
        for _ in range(10): cap.read()
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Cannot open camera")
            self.is_running = False
            return

        # Initial lock on center
        bbox = (center_x - 30, center_y - 30, 60, 60)
        tracker.init(frame, bbox)
        
        end_time = time.time() + (duration_minutes * 60)

        while self.is_running and time.time() < end_time:
            ret, frame = cap.read()
            if not ret: break

            success, bbox = tracker.update(frame)

            if success:
                x, y, w, h = [int(v) for v in bbox]
                obj_x = x + w // 2
                obj_y = y + h // 2
                
                # PID Control
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
                    if self.last_zone != "FORBIDDEN":
                        print(">> Violation!")
                        self.audio.speak("Please focus, do not look at your phone", "violation")
                        self.events_log.append({"type": "violation", "time": time.time()})
                        self.last_zone = "FORBIDDEN"
                elif tilt < self.SAFE_TILT:
                    if self.last_zone == "FORBIDDEN":
                        print(">> Back to focus")
                        self.audio.speak("Good job, keep it up", "safe")
                        self.last_zone = "SAFE"
            
            time.sleep(0.03) # CPU yield

        cap.release()
        self.controller.center()
        self.is_running = False
