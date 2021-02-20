from compas.geometry import closest_point_on_plane
from compas.geometry import distance_point_point_sqrd

from compas_cem.optimization.goals import Goal


__all__ = [
    "PlaneGoal"
]


class PlaneGoal(Goal):
    """
    Pulls the xyz position of a node to a target plane.
    """
    def __init__(self, node=None, plane=None):
        super(PlaneGoal, self).__init__(node, plane)

    def error(self, data):
        """
        The error between the xyz coords of a node and its closest point on a plane.

        Returns
        -------
        error : ``float``
            The squared distance between the two points.
        """
        point_a = self.reference(data)
        point_b = self.target(point_a)

        return distance_point_point_sqrd(point_a, point_b)

    def reference(self, data):
        """
        """
        a = data["node_xyz"][self.key()]

        return a

    def target(self, point):
        """
        """
        plane = self._target

        return closest_point_on_plane(point, plane)


if __name__ == "__main__":
    pass
