
from math import tan, ceil, pi, sqrt
from ..geometry import Surface2D

class WheelEncoder(object):
    def __init__(self, sensor_type, radius, length, ticks_per_rev):
        self._type = sensor_type
        self._radius = radius
        self._length = length
        self.ticks_per_rev = ticks_per_rev
        self.ticks = 0

    def update_ticks(self, wheel_velocity, time_delta):
        self.ticks += self._distance_to_ticks(wheel_velocity * time_delta.total_seconds())

    def reset_ticks(self):
        self.ticks = 0

    def _distance_to_ticks(self, distance):
        return ceil((distance * self.ticks_per_rev) / (2*pi))

    def _ticks_to_distance(self, ticks):
        return (ticks * 2 * pi) / self.ticks_per_rev


class ProximitySensor(object):
    def __init__(self, sensor_type, pose, r_min, r_max, phi, distance_to_raw=lambda x: x):
        self._type = sensor_type
        self._location = pose

        self._range = r_max
        self._spread = phi
        
        self.max_range = r_max
        self._min_range = r_min
        
        self._distance_to_raw = distance_to_raw

    def get_bounds(self):
        r = self._range
        r1 = r * tan(self._spread / 4)
        r2 = r * tan(self._spread / 2)
        return Surface2D(self._location, [
            (0, 0),
            (sqrt(r ** 2 - r2 ** 2), r2),
            (sqrt(r ** 2 - r1 ** 2), r1),
            (r, 0),
            (sqrt(r ** 2 - r1 ** 2), -r1),
            (sqrt(r ** 2 - r2 ** 2), -r2)
        ])

    def get_surfaces(self):
        # if (distance < self.max_range)
        #     set(surface.handle_, 'EdgeColor', 'r');
        #     set(surface.handle_, 'FaceColor', [1 0.8 0.8]);
        # else
        #     set(surface.handle_, 'EdgeColor', 'b')
        #     set(surface.handle_, 'FaceColor', [0.8 0.8 1]);
        # end

        return [
            (self.get_bounds(), '#ccccff')
        ]

    def update_range(self, distance):
        self._range = self._limit_to_sensor(distance)
        
    def get_range(self):
        return self._distance_to_raw(self._range)

    def _limit_to_sensor(self, distance):
        return min(max(distance, self._min_range), self.max_range)
