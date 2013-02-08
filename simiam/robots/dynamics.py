
from math import cos, sin
from ..geometry import Pose2D

class DifferentialDrive(object):
    def __init__(self, wheel_radius, wheel_base_length):
        self._wheel_radius = wheel_radius
        self._wheel_base_length = wheel_base_length
    
    def apply_dynamics(self, pose_t, time_delta, vel_r, vel_l):
        R = self._wheel_radius
        L = self._wheel_base_length
                
        v = R / 2 * (vel_r + vel_l)
        w = R / L * (vel_r - vel_l)

        # options = odeset('RelTol',1e-8,'AbsTol',1e-8);
        # [t,z] = ode45(@self._dynamics, [0 dt], [x_k, y_k, theta_k, v, w], options);
        # pose_t_1 = simiam.ui.Pose2D(z(end,1),z(end,2),z(end,3));

        x_k_1 = pose_t.x + time_delta * (v * cos(pose_t.theta))
        y_k_1 = pose_t.y + time_delta * (v * sin(pose_t.theta))
        theta_k_1 = pose_t.theta + time_delta * w
        
        return Pose2D(x_k_1, y_k_1, theta_k_1)
    
    # function dz = dynamics(obj, t, z)
    #     dz = zeros(5,1);
    #     dz(1:2) = z(4)*[cos(z(3));sin(z(3))];
    #     dz(3) = z(5);
    # end
    
    def uni_to_diff(self, v, w):
        R = self._wheel_radius
        L = self._wheel_base_length
        
        return (
            v / R + (w * L) / (2 * R),
            v / R - (w * L) / (2 * R)
        )
    
    def diff_to_uni(self, r, l):
        R = self._wheel_radius
        L = self._wheel_base_length
        
        return (
            R / 2 * (r + l),
            R / L * (r - l)
        )
