
import xml.etree.ElementTree as ET
from geometry import Pose2D, Surface2D
import applications
import robots
import controllers


class Obstacle(Surface2D):
    def __init__(self, pose, geometry):
        Surface2D.__init__(self, pose, geometry)


class World(object):
    def __init__(self):
        self.application = None
        self.robots = []
        self.obstacles = []

    def _lookup_class(self, module, name):
        return reduce(getattr, name.split('.'), module)

    def build_from_file(self, filename):
        blueprint = ET.parse(filename).getroot()

        app = blueprint.find('./app').get('type')
        self.application = self._lookup_class(applications, app)()

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
        self.robots.append({
            'robot': robot,
            'controller': controller,
            'pose': pose
        })

        self.application.add_controller(controller)

    def add_obstacle(self, pose, geometry):
        self.obstacles.append(Obstacle(pose, geometry))


class Simulator(object):
    def __init__(self, world, time_step):
        self._time_step = time_step
        self._world = world
        #self._physics = Physics(world)

    def step(self):
        for robot in self._world.robots:
            robot['controller'].execute(self._time_step)
            robot['pose'] = robot['robot'].update_state(robot['pose'], self._time_step.total_seconds())

        self._world.application.run(self._time_step)
        #self._physics.apply_physics()
