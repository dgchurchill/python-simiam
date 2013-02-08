
from basic import Controller
from ..geometry import Pose2D

class Supervisor(object):
    def __init__(self):
        self._controllers = [ Controller('default') ]
        self._current_controller = self._controllers[0]
        self._robot = []
        self._state_estimate = Pose2D()

    def attach_robot(self, robot, pose):
        self._robot = robot
        self._state_estimate = pose
