
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
        a = self._edge_set
        b = other._edge_set

        n_a = len(a)
        n_b = len(b)

        m_x_1 = [x[0][0] for x in a]
        m_x_2 = [x[1][0] for x in a]
        m_x_3 = [x[0][0] for x in b]
        m_x_4 = [x[1][0] for x in b]

        m_y_1 = [x[0][1] for x in a]
        m_y_2 = [x[1][1] for x in a]
        m_y_3 = [x[0][1] for x in b]
        m_y_4 = [x[1][1] for x in b]

        m_y_13 = [operator.sub(*x) for x in zip(m_y_1, m_y_3)]
        m_x_13 = [operator.sub(*x) for x in zip(m_x_1, m_x_3)]
        m_x_21 = [operator.sub(*x) for x in zip(m_x_2, m_x_1)]
        m_y_21 = [operator.sub(*x) for x in zip(m_y_2, m_y_1)]
        m_x_43 = [operator.sub(*x) for x in zip(m_x_4, m_x_3)]
        m_y_43 = [operator.sub(*x) for x in zip(m_y_4, m_y_3)]
   
        a1 = [operator.mul(*x) for x in zip(m_x_43, m_y_13)]
        a2 = [operator.mul(*x) for x in zip(m_y_43, m_x_13)]
        n_edge_a = [operator.sub(*x) for x in zip(a1, a2)]
   
        b1 = [operator.mul(*x) for x in zip(m_x_21, m_y_13)]
        b2 = [operator.mul(*x) for x in zip(m_y_21, m_x_13)]
        n_edge_b = [operator.sub(*x) for x in zip(b1, b2)]
   
        ab1 = [operator.mul(*x) for x in zip(m_y_43, m_x_21)]
        ab2 = [operator.mul(*x) for x in zip(m_x_43, m_y_21)]
        d_edge_ab = [operator.sub(*x) for x in zip(ab1, ab2)]

        u_a = [operator.div(*x) for x in zip(n_edge_a, d_edge_ab)]
        u_b = [operator.div(*x) for x in zip(n_edge_b, d_edge_ab)]
        
        ix_1 = [operator.mul(*x) for x in zip(m_x_21, u_a)]        
        intersect_set_x = [operator.add(*x) for x in zip(m_x_1, ix_1)]

        iy_1 = [operator.mul(*x) for x in zip(m_y_21, u_a)]        
        intersect_set_y = [operator.add(*x) for x in zip(m_y_1, iy_1)]

        points = []
        for i in range(len(u_a)):
            if u_a[i] >= 0 and u_a[i] <= 1 and u_b[i] >= 0 and u_b[i] <= 1:
                points.append((intersect_set_x[i], intersect_set_y[i]))

        return points
