import xml.etree.ElementTree as ET
from math import sqrt, sin, cos
import operator
import applications
import robots
import controllers


class Pose2D(object):
    def __init__(self, x, y, theta):
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
        for i in range(u_a):
            if u_a[i] >= 0 and u_a[i] <= 1 and u_b[i] >= 0 and u_b[i] <= 1:
                points.append((intersect_set_x[i], intersect_set_y[i]))

        return points


class Obstacle(Surface2D):
    def __init__(self, pose, geometry):
        Surface2D.__init__(self, pose, geometry)


class World(object):
    def __init__(self):
        self._application = None
        self._robots = []
        self.obstacles = []

    def _lookup_class(self, module, name):
        return reduce(getattr, name.split('.'), module)

    def build_from_file(self, filename):
        blueprint = ET.parse(filename).getroot()

        app = blueprint.find('./app').get('type')
        self._application = self._lookup_class(applications, app)()

        def get_float(node, name):
            return float(node.get(name))

        def get_pose(node):
            pose_node = node.find('./pose')
            return Pose2D(*[get_float(pose_node, n) for n in ['x', 'y', 'theta']])

        for robot_node in blueprint.findall('./robot'):
            robot_type = robot_node.get('type')
            supervisor = robot_node.find('./supervisor').get('type')
            pose = get_pose(robot_node)
            self.add_robot(robot_type, supervisor, pose)

        for obstacle_node in blueprint.findall('./obstacle'):
            pose = get_pose(obstacle_node)
            points = obstacle_node.findall('./geometry/point')
            geometry = [(get_float(p, 'x'), get_float(p, 'y')) for p in points]
            self.add_obstacle(pose, geometry)

    def add_robot(self, robot_type, supervisor, pose):
        robot = self._lookup_class(robots, robot_type)(pose)
        controller = self._lookup_class(controllers, supervisor)()
        controller.attach_robot(robot, pose)
        self._robots.append({
            'robot': robot,
            'controller': controller,
            'pose': pose
        })

        self._application.add_controller(controller)

    def add_obstacle(self, pose, geometry):
        self.obstacles.append(Obstacle(pose, geometry))
