from math import sqrt, pi, sin, cos
from supervisor import Supervisor
from basic import AvoidObstacles, GoToGoal, AOAndGTG
from ..geometry import Pose2D

class K3Supervisor(Supervisor):
    def __init__(self):
        Supervisor.__init__(self)

        self._controllers = [
            AvoidObstacles(),
            GoToGoal(),
            AOAndGTG()
        ]

        self._current_controller = self._controllers[1]

        self._prev_ticks = {
            'left': 0,
            'right': 0
        }

        self.goal = (0, 0)
        self.reached_goal = False

    def execute(self, time_delta):
        """
        Select and execute the current controller.

        See also controller/execute
        """
        x_distance = self._state_estimate.x - self.goal[0]
        y_distance = self._state_estimate.y - self.goal[1]

        print self.goal

        if sqrt(x_distance ** 2 + y_distance ** 2) > 0.02:
            outputs = self._current_controller.execute(
                self._robot,
                self._state_estimate,
                time_delta,
                x_g=self.goal[0],
                y_g=self.goal[1],
                v=0.1,
                d_c=0.08,
                d_s=0.1)

            w_r, w_l = self._robot.dynamics.uni_to_diff(outputs['v'], outputs['w'])
            print "x", w_r, w_l
            self._robot.set_wheel_speeds(w_r, w_l)
        else:
            self.reached_goal = True
            self._robot.set_wheel_speeds(0, 0)

        self._update_odometry()

    def _update_odometry(self):
        """
        Approximate the location of the robot.

        This method should be called from the
        execute function every iteration. The location of the robot is
        updated based on the difference to the previous wheel encoder
        ticks. This is only an approximation.
     
        _state_estimate is updated with the new location and the
        measured wheel encoder tick counts are stored in _prev_ticks.
        """

        # Get wheel encoder ticks from the robot
        right_ticks = self._robot.encoders[0].ticks
        left_ticks = self._robot.encoders[1].ticks
                
        prev_right_ticks = self._prev_ticks['right']
        prev_left_ticks = self._prev_ticks['left']
        
        self._prev_ticks['right'] = right_ticks
        self._prev_ticks['left'] = left_ticks
        
        # Previous estimate
        x = self._state_estimate.x
        y = self._state_estimate.y
        theta = self._state_estimate.theta
        
        # Compute odometry here
        
        m_per_tick = (2 * pi * self._robot.wheel_radius) / self._robot.encoders[0].ticks_per_rev
        
        d_right = (right_ticks - prev_right_ticks) * m_per_tick
        d_left = (left_ticks - prev_left_ticks) * m_per_tick
        
        d_center = (d_right + d_left) / 2
        phi = (d_right - d_left) / self._robot.wheel_base_length
        
        theta_p = theta + phi
        x_p = x + d_center * cos(theta)
        y_p = y + d_center * sin(theta)
                       
#             fprintf('Estimated pose (x,y,theta): (%0.3g,%0.3g,%0.3g)\n', x_p, y_p, theta_p);
        
        # Update your estimate of (x,y,theta)
        self._state_estimate = Pose2D(x_p, y_p, theta_p)
