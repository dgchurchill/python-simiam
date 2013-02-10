
import xml.etree.ElementTree as ET
from math import sqrt
from geometry import Pose2D, Surface2D
import applications
import robots
import controllers


class Obstacle(Surface2D):
    def __init__(self, pose, geometry):
        Surface2D.__init__(self, pose, geometry)

    def get_bounds(self):
        return self


class World(object):
    def __init__(self):
        self.application = None
        self.robots = []
        self.controllers = []
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

        self.robots.append(robot)
        self.controllers.append(controller)

        self.application.add_controller(controller)

    def add_obstacle(self, pose, geometry):
        self.obstacles.append(Obstacle(pose, geometry))


class Physics(object):
    def __init__(self, world):
        self._world = world

    def apply_physics(self):
        if self._body_collision_detection():
            return True

        self._proximity_sensor_detection()
        return False

    def _body_collision_detection(self):
        for robot in self._world.robots:
            robot_bounds = robot.get_bounds()
            
            # check against obstacles
            for obstacle in self._world.obstacles:
                obstacle_bounds = obstacle.get_bounds()

                if robot_bounds.precheck_surface(obstacle_bounds):
                    points = robot_bounds.intersection_with_surface(obstacle_bounds)
                    if len(points) > 0:
                        print 'COLLISION!'
                        return True
            
            # check against other robots
            for other_robot in self._world.robots:
                if other_robot == robot:
                    continue

                other_robot_bounds = other_robot.get_bounds()

                if robot_bounds.precheck_surface(other_robot_bounds):
                    points = robot_bounds.intersection_with_surface(other_robot_bounds)
                    if len(points) > 0:
                        print 'COLLISION!'
                        return True

        return False

    def _proximity_sensor_detection(self):
        for robot in self._world.robots:
            for ir_sensor in robot.ir_sensors:
                ir_bounds = ir_sensor.get_bounds()
                d_min = ir_sensor.max_range
                ir_sensor.update_range(d_min)

                # check against obstacles
                for obstacle in self._world.obstacles:
                    obstacle_bounds = obstacle.get_bounds()
                    
                    if ir_bounds.precheck_surface(obstacle_bounds):
                        d_min = self._update_proximity_sensor(ir_sensor, ir_bounds, obstacle_bounds, d_min)
                        print "d1", d_min

                # check against other robots
                for other_robot in self._world.robots:
                    if other_robot == robot:
                        continue

                    other_robot_bounds = other_robot.get_bounds()
                    
                    if ir_bounds.precheck_surface(other_robot_bounds):
                        d_min = self._update_proximity_sensor(ir_sensor, ir_bounds, other_robot_bounds, d_min)
                        print "d2", d_min
                
                if d_min < ir_sensor.max_range:
                    print "update", d_min
                    ir_sensor.update_range(d_min)

    def _update_proximity_sensor(self, sensor, sensor_bounds, obstacle_bounds, d_min):
        points = sensor_bounds.intersection_with_surface(obstacle_bounds)
        for point in points:
#            d = norm(pt-sensor_surface.geometry_(1,1:2));
            d = sqrt((point[0] - sensor_bounds.geometry[0][0]) ** 2 + (point[1] - sensor_bounds.geometry[0][1]) ** 2)
            d = sensor.limit_to_sensor(d)
            if d < d_min:
                d_min = d
        return d_min


class Simulator(object):
    def __init__(self, world, time_step):
        self._time_step = time_step
        self._world = world
        self._physics = Physics(world)

    def step(self):
        for controller in self._world.controllers:
            controller.execute(self._time_step)

        for robot in self._world.robots:
            robot.execute(self._time_step)

        self._world.application.run(self._time_step)

        self._physics.apply_physics()
