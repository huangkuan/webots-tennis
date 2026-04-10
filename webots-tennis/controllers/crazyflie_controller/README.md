# Ball Following Drone Controller

This project implements a Crazyflie drone controller in Webots that can follow a tennis ball using computer vision.

## Architecture

The system is split into two independent components to avoid dependency conflicts:

1. **Ball Detector Server** (`ball_detector.py`): Runs as a standalone UDP server with OpenCV and YOLOv8
2. **Drone Controller** (`crazyflie_wallfollowing.py`): Webots controller that communicates via UDP

## Setup

### 1. Ball Detector Environment
Create a separate Python environment for the ball detector:

```bash
# Create virtual environment
python3 -m venv ~/ball_detector_env
source ~/ball_detector_env/bin/activate

# Install dependencies (these require numpy >= 2.0)
pip install opencv-python numpy ultralytics
```

### 2. Webots Environment
Keep Webots using its default environment (which has numpy < 2.0).

## Usage

### Step 1: Start Ball Detector
In a separate terminal, run:

```bash
source ~/ball_detector_env/bin/activate
cd /path/to/kuandrone/controllers/crazyflie_wallfollowing
python run_ball_detector.py --visualize
```

This starts the UDP server on localhost:5005.

### Step 2: Start Webots Simulation
Open `kuandrone.wbt` in Webots and run the simulation. The drone controller will automatically connect to the ball detector.

### Step 3: Control
- **Arrow keys**: Manual flight control
- **Q/E**: Yaw rotation
- **W/S**: Altitude control
- **B**: Toggle ball following mode

When ball following is enabled, the drone will move toward detected tennis balls.

## Configuration

### Ball Detector
- `--host`: Server host (default: 127.0.0.1)
- `--port`: UDP port (default: 5005)
- `--model`: YOLO model (default: yolov8n.pt)
- `--camera`: Camera ID (default: 0)
- `--conf`: Confidence threshold (default: 0.5)
- `--visualize`: Show detection window

### Drone Controller
Edit constants in `crazyflie_wallfollowing.py`:
- `BALL_DETECTOR_HOST`: IP of ball detector server
- `BALL_DETECTOR_PORT`: UDP port
- `ball_center_threshold`: Pixel threshold for movement (default: 50)
- Max speed: 0.3 m/s (configurable)

## Troubleshooting

- **No ball detection**: Check camera permissions and that ball detector is running
- **Connection issues**: Verify UDP port is not blocked by firewall
- **Dependency conflicts**: Ensure separate environments for ball detector vs Webots</content>
<parameter name="filePath">/Users/huangkuan/Documents/Drone/kuandrone/controllers/crazyflie_wallfollowing/README.md