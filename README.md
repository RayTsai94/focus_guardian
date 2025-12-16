
# 專注力守門員 📱🎯
<img width="631" height="339" alt="image" src="https://github.com/user-attachments/assets/26b2133b-ab53-4cd8-89c2-07f05a6c108c" />
<img width="631" height="413" alt="image" src="https://github.com/user-attachments/assets/4315acd6-55b8-45d9-a821-ed01dcc7a597" />
<img width="1380" height="1756" alt="image" src="https://github.com/user-attachments/assets/2c14746f-1b34-493d-9c6f-12e0c9244e39" />

[![Focus Tracker Demo](https://img.youtube.com/vi/tIOz286DohM/maxresdefault.jpg)](https://youtube.com/shorts/tIOz286DohM?si=h_dDpBcybp6Eq0c6)

##assembly
<img width="780" height="633" alt="image" src="https://github.com/user-attachments/assets/1bf540db-fa24-442d-9eaf-13088ad09b48" />

A smart focus tracking system that uses computer vision to monitor phone usage during study/work sessions. The system tracks your phone's position and alerts you when it enters the "forbidden zone" (face area), encouraging better focus habits.

## Features

### Core Functionality
- **📷 Real-time Object Tracking**: Uses CSRT tracker to follow your phone's movement
- **🎯 Zone-based Monitoring**: Distinguishes between safe (desk) and forbidden (face) areas
- **🔊 Audio Feedback**: Voice alerts for violations and encouragements
- **📊 Session Logging**: Tracks distraction events and generates summaries
- **🎮 Motor Control**: Pan-tilt camera control for optimal tracking

### Web Interface
- **📺 Live Video Stream**: Real-time camera feed with tracking overlays
- **🎨 Visual Indicators**: Zone boundaries and tracking status display
- **📱 Responsive Design**: Works on desktop and mobile browsers

### LINE Bot Integration
- **💬 Chat Interface**: Start/stop sessions via LINE messaging
- **🤖 AI-powered**: Uses Google Gemini for intent parsing and summary generation
- **📈 Progress Reports**: Automated session summaries with encouragement

## System Requirements

### Hardware
- Raspberry Pi 4 (recommended) or compatible SBC
- Camera module (Pi Camera v2/v3 or compatible)
- Pan-tilt servo mechanism (optional)
- Speaker for audio feedback

### Software
- Python 3.8+
- Raspberry Pi OS or compatible Linux distribution
- Active internet connection for AI features

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd focus
```

### 2. Install Dependencies
```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### 3. Hardware Setup
```bash
# Enable camera interface
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable

# Reboot system
sudo reboot
```

### 4. Environment Configuration
Create a `.env` file with your credentials:
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
```
LINE_CHANNEL_ACCESS_TOKEN=your_line_bot_token
LINE_CHANNEL_SECRET=your_line_bot_secret
GEMINI_API_KEY=your_google_gemini_api_key
```

## Configuration

### Camera Settings
Edit `tracker.py` to adjust camera parameters:
```python
self.WIDTH, self.HEIGHT = 320, 240  # Resolution
self.SAFE_TILT = 80                 # Safe zone threshold
self.FORBIDDEN_TILT = 110           # Forbidden zone threshold
```

### PID Control Tuning
Adjust tracking responsiveness:
```python
self.Kp = 0.07        # Proportional gain
self.dead_zone = 30   # Movement threshold
```

### Audio Settings
Configure speech feedback in `audio_manager.py`:
```python
# Language and voice settings
self.lang = 'en'      # Language code
self.slow = False     # Speech speed
```

## Usage

### 1. Start the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Run the main application
python3 app.py
```

### 2. Access Web Interface
Open your browser and navigate to:
```
http://localhost:5000
```

### 3. LINE Bot Commands
Send messages to your LINE Bot:
- **"Start focus"** or **"Focus 30"** - Begin tracking session
- **"Stop"** or **"End"** - End current session

### 4. Camera Cleanup (if needed)
If you encounter camera busy errors:
```bash
./cleanup_camera.sh
```

## API Endpoints

### Web Routes
- `GET /` - Main dashboard with video stream
- `GET /video_feed` - MJPEG video stream endpoint

### LINE Bot Webhook
- `POST /callback` - LINE Bot webhook handler

## File Structure

```
focus/
├── app.py              # Main Flask application
├── tracker.py          # Core tracking logic
├── llm_service.py      # AI integration (Gemini)
├── audio_manager.py    # Speech synthesis
├── motor_control.py    # Servo control
├── pid_controller.py   # PID control algorithm
├── db_manager.py       # Database operations
├── PCA9685.py         # I2C servo driver
├── test_cam.py        # Camera testing utility
├── cleanup_camera.sh   # Camera resource cleanup
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── README.md          # This file
```

## Troubleshooting

### Camera Issues
```bash
# Check camera status
vcgencmd get_camera

# List video devices
ls /dev/video*

# Test camera
libcamera-hello --timeout 5000
```

### Common Errors

**"Camera __init__ sequence did not complete"**
```bash
# Run cleanup script
./cleanup_camera.sh

# Or manually reset
sudo pkill -f libcamera
sudo modprobe -r bcm2835-v4l2
sudo modprobe bcm2835-v4l2
```

**"Port 5000 is in use"**
```bash
# Find and kill process
lsof -i :5000
kill -9 <PID>
```

**Missing Python modules**
```bash
pip install -r requirements.txt
```

## Development

### Testing Individual Components

**Camera Test:**
```bash
python3 test_cam.py
```

**Tracker Test:**
```bash
python3 -c "from tracker import FocusTracker; t = FocusTracker(); t.start_tracking(1)"
```

### Adding New Features

1. **Custom Zones**: Modify zone thresholds in `tracker.py`
2. **New Audio Cues**: Add phrases in `audio_manager.py`
3. **Additional Webhooks**: Extend LINE Bot handlers in `app.py`

### Debug Mode
Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

### For Better Tracking
- Use adequate lighting
- Ensure phone contrast against background
- Position camera at optimal angle
- Adjust PID parameters for your setup

### For Smooth Streaming
- Reduce camera resolution if needed
- Adjust frame rate in `generate_frames()`
- Close unnecessary applications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV community for computer vision tools
- Raspberry Pi Foundation for hardware platform
- Google for Gemini AI API
- LINE Corporation for messaging platform

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review system logs
3. Test individual components
4. Create an issue with detailed error information

---

**Happy Focusing! 🎯📚**
