
from math import sqrt, sin, cos
import operator


class Pose2D(object):
    def __init__(self, x=0, y=0, theta=0):
        self.x = x
        self.y = y
        self.theta = theta

    def transform(self, points):
        s_t = sin(self.theta)
        c_t = cos(self.theta)

        return [(self.x + c_t * p[0] - s_t * p[1], self.y + s_t * p[0] + c_t * p[1]) for p in points]


class Surface2D(object):
    def __init__(self, pose, geometry):
        self._original_geometry = geometry
        self.set_pose(pose)

    def set_pose(self, pose):
        self.geometry = pose.transform(self._original_geometry)

        n = len(self.geometry)
        self._centroid = [sum(x) / n for x in zip(*self.geometry)]

        # twice the max distance from the centroid
        self._geometric_span = 2 * max(sqrt((x[0] - self._centroid[0]) ** 2 + (x[1] - self._centroid[1]) ** 2) for x in self.geometry)

        self._edge_set = zip(self.geometry, self.geometry[1:] + [self.geometry[0]])

    def precheck_surface(self, surface):
#        d = norm(self._centroid_-surface_b.centroid_);
        d = sqrt((self._centroid[0] - surface._centroid[0]) ** 2 + (self._centroid[1] - surface._centroid[1]) ** 2)
        return d < (self._geometric_span + surface._geometric_span) / sqrt(3)

    def intersection_with_surface(self, other):
        points = []

        for edge_a in self._edge_set:
            for edge_b in other._edge_set:
                x_13 = edge_a[0][0] - edge_b[0][0]
                y_13 = edge_a[0][1] - edge_b[0][1]

                x_21 = edge_a[1][0] - edge_a[0][0]
                y_21 = edge_a[1][1] - edge_a[0][1]

                x_43 = edge_b[1][0] - edge_b[0][0]
                y_43 = edge_b[1][1] - edge_b[0][1]

                n_edge_a = x_43 * y_13 - y_43 * x_13
                n_edge_b = x_21 * y_13 - y_21 * x_13
                d_edge_ab = y_43 * x_21 - x_43 * y_21

                if d_edge_ab == 0:
                    continue

                u_a = n_edge_a / d_edge_ab
                u_b = n_edge_b / d_edge_ab

                if u_a >= 0 and u_a <= 1 and u_b >= 0 and u_b <= 1:
                    points.append((edge_a[0][0] + x_21 * u_a, edge_a[0][1] + y_21 * u_a))

        return points
