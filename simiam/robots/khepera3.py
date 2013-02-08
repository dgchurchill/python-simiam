
from math import radians, floor
from robot import Robot
from sensor import WheelEncoder, ProximitySensor
from dynamics import DifferentialDrive
from ..geometry import Pose2D, Surface2D

class Khepera3(Robot):
    def __init__(self, initial_pose):
        # Add sensors: wheel encoders and IR proximity sensors
        self.wheel_radius = 0.021           # 42mm
        self.wheel_base_length = 0.0885     # 88.5mm
        self._ticks_per_rev = 2765
        self._speed_factor = 6.2953e-6
        self._pose = initial_pose
        
        self.encoders = [
            WheelEncoder('right_wheel', self.wheel_radius, self.wheel_base_length, self._ticks_per_rev),
            WheelEncoder('left_wheel', self.wheel_radius, self.wheel_base_length, self._ticks_per_rev)
        ]

        sensor_poses = [
            (-0.038, 0.048, 128),
            (0.019, 0.064, 75),
            (0.050, 0.050, 42),
            (0.070, 0.017, 13),
            (0.070, -0.017, -13),
            (0.050, -0.050, -42),
            (0.019, -0.064, -75),
            (-0.038, -0.048, -128),
            (-0.048, 0.000, 180)
        ]

        def ir_distance_to_raw(distance):
            if distance < 0.02:
                return 3960
            
            return ceil(3960 * exp(-30 * (distance - 0.02)))

        self._ir_sensors = [
            ProximitySensor(
                'IR',
                Pose2D(x[0], x[1], radians(x[2])),
                0.02,
                0.2,
                radians(20),
                ir_distance_to_raw) 
            for x in sensor_poses]
        
        # Add dynamics: two-wheel differential drive
        self.dynamics = DifferentialDrive(self.wheel_radius, self.wheel_base_length)
        
        self._right_wheel_speed = 0
        self._left_wheel_speed = 0


    def get_surfaces(self):
        # Khepera3 in top-down 2D view
        k3_top_plate = Surface2D(self._pose, [
            (-0.031,   0.043),
            (-0.031,  -0.043),
            ( 0.033,  -0.043),
            ( 0.052,  -0.021),
            ( 0.057,       0),
            ( 0.052,   0.021),
            ( 0.033,   0.043)
        ])
                      
        k3_base = Surface2D(self._pose, [
            (-0.024,   0.064),
            ( 0.033,   0.064),
            ( 0.057,   0.043),
            ( 0.074,   0.010),
            ( 0.074,  -0.010),
            ( 0.057,  -0.043),
            ( 0.033,  -0.064),
            (-0.025,  -0.064),
            (-0.042,  -0.043),
            (-0.048,  -0.010),
            (-0.048,   0.010),
            (-0.042,   0.043)
        ])
        
        return [
            (k3_base, '#cccccc'),
            (k3_top_plate, '#000000')
        ]

    def execute(self, time_delta):
        sf = self._speed_factor
        R = self.wheel_radius
        
        vel_r = self._right_wheel_speed * (sf / R)     # mm/s
        vel_l = self._left_wheel_speed * (sf / R)      # mm/s
        
        self._pose = self.dynamics.apply_dynamics(self._pose, time_delta, vel_r, vel_l)

        # self._update_pose(pose)
        
        # for ir_sensor in self._ir_sensors:
        #     ir_sensor.update_pose(pose)
        
        # update wheel encoders
        self.encoders[0].update_ticks(vel_r, time_delta)
        self.encoders[1].update_ticks(vel_l, time_delta)
    
    def set_wheel_speeds(self, vel_r, vel_l):
        vel_r, vel_l = self._limit_speeds(vel_r, vel_l)
        
        sf = self._speed_factor
        R = self.wheel_radius
        
        self._right_wheel_speed = floor(vel_r * (R / sf))
        self._left_wheel_speed = floor(vel_l * (R / sf))

    def _limit_speeds(self, vel_r, vel_l):
        # actuator hardware limits
        v, w = self.dynamics.diff_to_uni(vel_r, vel_l)
        v = max(min(v, 0.314), -0.3148)
        w = max(min(w, 2.276), -2.2763)
        return self.dynamics.uni_to_diff(v, w)
