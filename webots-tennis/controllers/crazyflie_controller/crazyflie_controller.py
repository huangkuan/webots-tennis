"""
file: crazyflie_controller.py
Controls the crazyflie and implements a wall following method in webots in Python

"""


from controller import Robot
from controller import Keyboard
from math import cos, sin
from pid_controller import pid_velocity_fixed_height_controller
import socket
import json


FLYING_ATTITUDE = 1

if __name__ == '__main__':

    import sys
    print("Webots Python:", sys.executable)
    print("sys.path:")
    for p in sys.path:
        print(" ", p)

    robot = Robot()
    timestep = int(robot.getBasicTimeStep())

    # Initialize motors
    m1_motor = robot.getDevice("m1_motor")
    m1_motor.setPosition(float('inf'))
    m1_motor.setVelocity(-1)
    m2_motor = robot.getDevice("m2_motor")
    m2_motor.setPosition(float('inf'))
    m2_motor.setVelocity(1)
    m3_motor = robot.getDevice("m3_motor")
    m3_motor.setPosition(float('inf'))
    m3_motor.setVelocity(-1)
    m4_motor = robot.getDevice("m4_motor")
    m4_motor.setPosition(float('inf'))
    m4_motor.setVelocity(1)

    # # Initialize Sensors
    imu = robot.getDevice("inertial_unit")
    imu.enable(timestep)
    gps = robot.getDevice("gps")
    gps.enable(timestep)
    gyro = robot.getDevice("gyro")
    gyro.enable(timestep)

    # # Get keyboard
    keyboard = Keyboard()
    keyboard.enable(timestep)

    # # Initialize variables
    past_x_global = 0
    past_y_global = 0
    past_time = 0
    first_time = True

    # # Crazyflie velocity PID controller
    PID_crazyflie = pid_velocity_fixed_height_controller()
    PID_update_last_time = robot.getTime()
    sensor_read_last_time = robot.getTime()

    height_desired = FLYING_ATTITUDE

    # # Set up UDP socket to communicate with ball detector server
    BALL_DETECTOR_HOST = '127.0.0.1'
    BALL_DETECTOR_PORT = 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((BALL_DETECTOR_HOST, BALL_DETECTOR_PORT))  # Bind to receive port
    sock.settimeout(0.01)  # Non-blocking with short timeout
    
    latest_detection = None
    ball_follow_enabled = False
    print("✓ UDP socket set up for ball detector communication on port", BALL_DETECTOR_PORT)
    print("- Press B to enable/disable ball following")
    ball_follow_speed_x = 0.0
    ball_follow_speed_y = 0.0
    ball_center_threshold = 50  # pixels from center to trigger movement

    print("\n")
    print("====== Controls =======\n\n")
    print(" The Kuan Drone can be controlled from your keyboard!\n")
    print(" All controllable movement is in body coordinates\n")
    print("- Use the up, back, right and left button to move in the horizontal plane\n")
    print("- Use Q and E to rotate around yaw\n ")
    print("- Use W and S to go up and down\n ")
    # print("- Press A to start autonomous mode\n")
    # print("- Press D to disable autonomous mode\n")

    # Main loop:
    try:
        while robot.step(timestep) != -1:

            dt = robot.getTime() - past_time
            actual_state = {}

            if first_time:
                past_x_global = gps.getValues()[0]
                past_y_global = gps.getValues()[1]
                past_time = robot.getTime()
                first_time = False

            # Get sensor data
            roll = imu.getRollPitchYaw()[0]
            pitch = imu.getRollPitchYaw()[1]
            yaw = imu.getRollPitchYaw()[2]
            yaw_rate = gyro.getValues()[2]
            x_global = gps.getValues()[0]
            v_x_global = (x_global - past_x_global)/dt
            y_global = gps.getValues()[1]
            v_y_global = (y_global - past_y_global)/dt
            altitude = gps.getValues()[2]

            # Get body fixed velocities
            cos_yaw = cos(yaw)
            sin_yaw = sin(yaw)
            v_x = v_x_global * cos_yaw + v_y_global * sin_yaw
            v_y = - v_x_global * sin_yaw + v_y_global * cos_yaw

            # Initialize values
            desired_state = [0, 0, 0, 0]
            forward_desired = 0
            sideways_desired = 0
            yaw_desired = 0
            height_diff_desired = 0

            key = keyboard.getKey()
            while key > 0:
                if key == Keyboard.UP:
                    forward_desired += 0.5
                elif key == Keyboard.DOWN:
                    forward_desired -= 0.5
                elif key == Keyboard.RIGHT:
                    sideways_desired -= 0.5
                elif key == Keyboard.LEFT:
                    sideways_desired += 0.5
                elif key == ord('Q'):
                    yaw_desired = + 1
                elif key == ord('E'):
                    yaw_desired = - 1
                elif key == ord('W'):
                    height_diff_desired = 0.1
                elif key == ord('S'):
                    height_diff_desired = - 0.1
                elif key == ord('B'):
                    ball_follow_enabled = not ball_follow_enabled
                    status = "ON" if ball_follow_enabled else "OFF"
                    print(f"Ball following: {status}")
                key = keyboard.getKey()

            height_desired += height_diff_desired * dt

            # Read ball detection from UDP socket
            try:
                data, addr = sock.recvfrom(4096)
                latest_detection = json.loads(data.decode('utf-8'))
                #print(f"Received ball detection: {latest_detection}")
            except (socket.timeout, json.JSONDecodeError, ConnectionResetError):
                pass  # No response or invalid data, keep previous detection

            # Ball following logic
            if ball_follow_enabled and latest_detection is not None:
                # Check if ball was detected (has 'x' and 'y' fields)
                if 'x' in latest_detection and 'y' in latest_detection:
                    # Camera frame is 1280x720 (from main_live_kuan.py source)
                    frame_width = 1280
                    frame_height = 720
                    ball_x = latest_detection['x']
                    ball_y = latest_detection['y']

                    # Calculate offset from frame center
                    offset_x = ball_x - frame_width / 2.0
                    offset_y = ball_y - frame_height / 2.0

                    # Map to velocity commands (normalized)
                    if abs(offset_x) > ball_center_threshold:
                        # Left/right: ball's X position (left = left, right = right)
                        ball_follow_speed_y = offset_x / (frame_width / 2.0) * 0.3
                    else:
                        ball_follow_speed_y = 0.0

                    if abs(offset_y) > ball_center_threshold:
                        # Forward/backward: ball's Y position (top = away, bottom = toward)
                        ball_follow_speed_x = -offset_y / (frame_height / 2.0) * 0.3
                    else:
                        ball_follow_speed_x = 0.0

                    # Apply ball following velocities
                    forward_desired = ball_follow_speed_x
                    sideways_desired = ball_follow_speed_y
                else:
                    # Ball lost, stop movement
                    forward_desired = 0.0
                    sideways_desired = 0.0

            # PID velocity controller with fixed height
            motor_power = PID_crazyflie.pid(dt, forward_desired, sideways_desired,
                                            yaw_desired, height_desired,
                                            roll, pitch, yaw_rate,
                                            altitude, v_x, v_y)

            m1_motor.setVelocity(-motor_power[0])
            m2_motor.setVelocity(motor_power[1])
            m3_motor.setVelocity(-motor_power[2])
            m4_motor.setVelocity(motor_power[3])

            past_time = robot.getTime()
            past_x_global = x_global
            past_y_global = y_global
    finally:
        sock.close()
        print("✓ UDP socket closed")
