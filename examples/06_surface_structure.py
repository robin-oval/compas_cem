import os

from time import time
from math import pi
from math import cos
from math import sin
from statistics import mean

import numpy as np

from compas.geometry import Translation

from compas.datastructures import mesh_dual

from compas_singular.datastructures import CoarseQuadMesh

from compas_cem.diagrams import TopologyDiagram

from compas_cem.loads import NodeLoad

from compas_cem.equilibrium import static_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import TrailEdgeParameter, DeviationEdgeParameter
from compas_cem.optimization import TrailEdgeForceConstraint, PlaneConstraint

from compas_plotters.plotter import Plotter
from compas_view2.app import App


# ------------------------------------------------------------------------------
# Create a topology diagram
# ------------------------------------------------------------------------------


HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, 'data/coarse_quad_mesh_66.json')
coarse = CoarseQuadMesh.from_json(FILE)
print('coarse quad mesh:', coarse)

coarse.collect_strips()
coarse.set_strips_density(4)
coarse.densification()
mesh = coarse.get_quad_mesh()
print('dense quad mesh:', mesh)

mesh = mesh_dual(mesh)
print('dual quad mesh:', mesh)
FILE = os.path.join(HERE, 'data/shell_topology.json')
mesh.to_json(FILE)

supports = []
boundary_vertices = mesh.vertices_on_boundary()[:-1]
for i in range(len(boundary_vertices)):
    u, v = boundary_vertices[0:2]
    polyedge = mesh.collect_polyedge(u, v)
    if i % 2 == 0:
        supports += polyedge
        for _ in range(len(polyedge)):
            del boundary_vertices[0]
    else:
        for _ in range(len(polyedge) - 2):
            del boundary_vertices[0]
    if len(boundary_vertices) == 0:
        break
print(len(supports), 'supports')

mean_length = mean([mesh.edge_length(*edge) for edge in mesh.edges()])

topology = TopologyDiagram.from_dualquadmesh(
    mesh, supports, trail_length=-mean_length, deviation_force=-1.0)
topology.build_trails()

for key in topology.nodes():
    topology.add_load(NodeLoad(key, [0.0, 0.0, -0.1]))

# ------------------------------------------------------------------------------
# Compute a state of static equilibrium
# ------------------------------------------------------------------------------

form = static_equilibrium(topology, eta=1e-6, tmax=100)

FILE = os.path.join(HERE, 'data/shell_form_found.json')
form.to_json(FILE)

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

# # create optimizer
# opt = Optimizer()

# # parameters
# for edge in topology.trail_edges():
#     opt.add_parameter(TrailEdgeParameter(edge, -1.0, -1.0))

# for edge in topology.deviation_edges():
#     opt.add_parameter(DeviationEdgeParameter(edge, -1.0, -0.1))

# # constraints
# for edge in topology.trail_edges():
#     opt.add_constraint(TrailEdgeForceConstraint(edge, -1.0))

# for vkey in supports:
#     opt.add_constraint(PlaneConstraint(vkey, plane=((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))))

# # optimize
# start = time()
# form_opt = opt.solve_nlopt(topology, algorithm="LBFGS", iters=500, eps=1e-3)

# # print out results
# print("----------")
# print(f"Optimizer. # Parameters {opt.number_of_parameters()}, # Constraints {opt.number_of_constraints()}")
# print(f"Optimization elapsed time: {time() - start}")
# print(f"Final value of the objective function: {opt.penalty}")
# print(f"Norm of the gradient of the objective function: {opt.gradient_norm}")

# FILE = os.path.join(HERE, 'data/shell_form_opt.json')
# form_opt.to_json(FILE)

# ------------------------------------------------------------------------------
# Plot results
# ------------------------------------------------------------------------------

# ns = 0.45
# shift = 1.0
# plotter = Plotter(figsize=(16.0, 9.0))

# # plot topology diagram
# plotter.add(topology, nodesize=ns)

# # plot translated form diagram
# T = Translation.from_vector([shift, 0.0, 0.0])
# plotter.add(form.transformed(T), nodesize=ns)

# # plot translated optimized form diagram
# T = Translation.from_vector([shift * 2.0, 0.0, 0.0])
# plotter.add(form_opt.transformed(T), nodesize=ns)

# # show scene
# plotter.zoom_extents(padding=-0.3)
# plotter.show()

# viewer = App(width=1600, height=900)
# viewer.view.camera.rx = -60
# viewer.view.camera.rz = 0
# viewer.view.camera.ty = -2
# viewer.view.camera.distance = 10

# viewer.add(form)
# viewer.show()
