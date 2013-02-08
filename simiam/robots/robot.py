
class Robot(object):
    def attach_supervisor(self, supervisor):
        self._supervisor = supervisor
        supervisor.attach_robot(self)
