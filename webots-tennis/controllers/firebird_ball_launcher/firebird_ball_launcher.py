"""Simple tennis ball launcher for the FireBird6 in Webots.

The controller waits briefly for the simulation to start, places the tennis
ball near the FireBird6, resets its physics, and launches it across the court.
"""

from controller import Supervisor


robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

ball = robot.getFromDef("TENNIS_BALL")
ball_right = robot.getFromDef("TENNIS_BALL_RIGHT")
ball_backspin = robot.getFromDef("TENNIS_BALL_BACKSPIN")
if ball is None or ball_right is None or ball_backspin is None:
    raise RuntimeError("Tennis ball node not found in world.")

ball_translation = ball.getField("translation")
ball_right_translation = ball_right.getField("translation")
ball_backspin_translation = ball_backspin.getField("translation")

launch_state = 0
second_launch_time = None
third_launch_time = None

while robot.step(timestep) != -1:
    if launch_state == 6:
        continue

    # Give the world one moment to settle before launching.
    if robot.getTime() < 1.0:
        continue

    if launch_state == 0:
        # Place the ball first and clear any old momentum/collisions.
        ball_translation.setSFVec3f([0.0, 11.2, 0.38])
        ball.resetPhysics()
        launch_state = 1
        continue

    if launch_state == 1:
        # Left topspin ball: slower initial travel, higher arc, stronger kick forward after bounce.
        ball.setVelocity([-2.6, -20.2, 4.2, 85.0, 0.0, 0.0])
        second_launch_time = robot.getTime() + 1.5
        launch_state = 2
        continue

    if launch_state == 2 and robot.getTime() >= second_launch_time:
        ball_right_translation.setSFVec3f([0.0, 11.2, 0.38])
        ball_right.resetPhysics()
        launch_state = 3
        continue

    if launch_state == 3:
        # Right topspin ball mirrors the left shot.
        ball_right.setVelocity([2.6, -20.2, 4.2, 85.0, 0.0, 0.0])
        third_launch_time = robot.getTime() + 1.5
        launch_state = 4
        continue

    if launch_state == 4 and robot.getTime() >= third_launch_time:
        ball_backspin_translation.setSFVec3f([0.0, 11.2, 0.38])
        ball_backspin.resetPhysics()
        launch_state = 5
        continue

    if launch_state == 5:
        # Linear velocity plus angular velocity around x for backspin.
        ball_backspin.setVelocity([1.0, -25.0, 3.8, -35.0, 0.0, 0.0])
        launch_state = 6
