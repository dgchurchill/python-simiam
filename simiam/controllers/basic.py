
from math import radians, atan2, cos, sin, sqrt, log
from ..geometry import Pose2D

class Controller(object):
    def __init__(self, type):
        self._type = type


class AvoidObstacles(Controller):
    def __init__(self):
        Controller.__init__(self, 'avoid_obstacles')

        self._sensor_poses = [Pose2D(theta=radians(x)) for x in [128, 75, 42, 13, -13, -42, -75, -128, 180]]

    def _sensor_to_distance(self, raw):
        return [(log(x / 3960) / -30) + 0.02 for x in raw]

    def execute(self, robot, state_estimate, time_delta, **inputs):
        # Poll the current IR sensor values 1-9
        ir_array_values = [max(x, 18) for x in robot.ir_array.get_range()]
            
        # Interpret the IR sensor measurements geometrically
        def raw_to_vector(pose, raw):
            return pose.transform([(self._sensor_to_distance(raw), 0)])

        ir_vectors = map(raw_to_vector, self._sensor_poses, ir_array_values)
        robot_orientation = Pose2D(theta=state_estimate.theta)
        ir_vectors = robot_orientation.transform(ir_vectors)

        # Compute the heading vector
        gains = [2 * x for x in [0, 1, 4, 5, 5, 4, 1, 0, 0]]

        u_i = map(lambda p, g: (p[0] * g, p[1] * g), ir_vectors, gains)
        u_1 = sum(x[0] for x in u_i)
        u_2 = sum(x[1] for x in u_i)
        norm_u = sqrt(u_1 ** 2 + u_2 ** 2)

        theta_d = atan2(u_2, u_1)
            
        # Compute the control
        
        k_v =  0.025
        k_w = 1.75
            
        v = k_v * norm_u * cos(theta_d - theta)
        w = k_w * norm_u * sin(theta_d - theta)
        
        v = inputs['v']
            
#             fprintf('(v,w) = (%0.4g,%0.4g)\n', v,w);
            
        # Transform from v,w to v_r,v_l and set the speed of the robot
#             [vel_r, vel_l] = self._uni_to_diff(robot,v,w);
#             robot.set_speed(vel_r, vel_l);

        return {
            'v': v,
            'w': w
        }


class GoToGoal(Controller):
    def __init__(self):
        Controller.__init__(self, 'go_to_goal')

        self._k_p = 10
        self._k_i = 0
        self._k_d = 0

        self._e_k = 0
        self._e_k_1 = 0

    def execute(self, robot, state_estimate, time_delta, **inputs):
        """
        Compute the left and right wheel speeds for go-to-goal.

        The method will compute the
        necessary linear and angular speeds that will steer the robot
        to the goal location (x_g, y_g) with a constant linear velocity
        of v.
        
        See also controller/execute
        """
        
        # Retrieve the (relative) goal location
        x_g = inputs['x_g']
        y_g = inputs['y_g']
            
        # Get estimate of current pose
        x = state_estimate.x
        y = state_estimate.y
        theta = state_estimate.theta
            
        # Compute the v,w that will get you to the goal
        v = inputs['v']
        
        # desired (goal) heading
        dx = x_g - x
        dy = y_g - y
        
        theta_d = atan2(dy, dx)
        
        # heading error
        e_k = theta_d - theta
        e_k = atan2(sin(e_k), cos(e_k))
        
        dt = time_delta.total_seconds()
        # PID for heading
        w = self._k_p * e_k + self._k_i * (self._e_k + e_k * dt) + self._k_d * (e_k - self._e_k_1) / dt
        
        # save errors
        self._e_k += e_k * dt
        self._e_k_1 = e_k
        
        # stop when sufficiently close
        delta = sqrt(dx ** 2 + dy ** 2)
        
        if delta < 0:  # wtf?
           v = 0
           w = 0

        return {
            'v': v,
            'w': w
        }        


class AOAndGTG(Controller):
    def __init__(self):
        Controller.__init__(self, 'ao_and_gtg')

        self._sensor_poses = [Pose2D(theta=radians(x)) for x in [128, 75, 42, 13, -13, -42, -75, -128, 180]]

        # initialize memory banks
        self._Kp = 10
        self._Ki = 0
        self._Kd = 0
        
        self._E_k = 0
        self._e_k_1 = 0


    def execute(self, robot, state_estimate, time_delta, **inputs):
        # Set the goal location
        x_g = inputs['x_g']
        y_g = inputs['y_g']
        
        d_c = inputs['d_c']
        d_s = inputs['d_s']
        
        v = inputs['v']
        
        # Update the odometry
        d_obs, theta_obs = self._closest_obstacle(robot, state_estimate)
            
        # Avoid obstacle controller
        
        # Compute the heading theta_d_ao that steers
        # the robot away from the obstacles
        
        theta_d_ao = theta_obs
        theta_d_ao = atan2(sin(theta_d_ao), cos(theta_d_ao))
        
        # Compute the heading theta_d_gtg that steers
        # the robot towards the goal
        
        dx = x_g - state_estimate.x
        dy = y_g - state_estimate.y
        theta_d_gtg = atan2(dy, dx) # Hint: x_g, and y_g can be useful here.
        
        # Blend the two heading vectors
                    
        if d_obs >= d_s:
            alpha = 0
        elif d_obs <= d_c:
            alpha = 1
        else:
            m = -1 / (d_s - d_c)
            b = 1 - m * d_c
            alpha = m * d_obs + b
                    
        theta_d = alpha * theta_d_ao + (1 - alpha) * theta_d_gtg
        
        # Compute the control
        
        # heading error
        e_k = theta_d - state_estimate.theta
        e_k = atan2(sin(e_k), cos(e_k))
        
        # PID for heading
        dt = time_delta.total_seconds()
        w = self._Kp * e_k + self._Ki * (self._E_k + e_k * dt) + self._Kd * (e_k - self._e_k_1) / dt
        
        # save errors
        self._E_k += e_k * dt
        self._e_k_1 = e_k
        
        return {
            'v': v,
            'w': w
        }

    def _closest_obstacle(self, robot, state_estimate):    
        # Interpret the IR sensor measurements geometrically
        
        ir_values = [max(x.get_range(), 18) for x in robot.ir_sensors]

        raw_to_distance = lambda raw: (log(raw / 3960) / -30) + 0.02

        ir_vectors = [[raw_to_distance(x), 0] for x in ir_values]

        # make sure that the rear IRs are ignored.
        for i in [0, 7, 8]:
            ir_vectors[i][0] = 0.3


        ir_vectors = [v for x in zip(self._sensor_poses, ir_vectors) for v in x[0].transform([x[1]])]
        ir_vectors = Pose2D(theta=state_estimate.theta).transform(ir_vectors)
        
        # Compute the vector to the closest obstacle
        
        dists = [sqrt(x[0] ** 2 + x[1] ** 2) for x in ir_vectors]

        i, m = min(enumerate(dists), key=lambda x: x[1])

        d_obs = m
        # Compute the heading vector
        
#             gains = -[0 1 1 1 1 1 1 0 0];
        gains = [2 * x for x in [0, 1, 4, 5, 5, 4, 1, 0, 0]]
        
        g_vectors = map(lambda g, x: [g * x[0], g * x[1]], gains, ir_vectors)
        u = [sum(x) for x in zip(*g_vectors)]
        
        theta_obs = atan2(u[1], u[0])

#             fprintf('closest obstacle: %0.3g,%0.3g\n', d_obs, simiam.ui.Pose2D.rad2deg(theta_obs));
        return (d_obs, theta_obs)
