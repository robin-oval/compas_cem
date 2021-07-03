import os
import matplotlib.pyplot as plt

from time import time

from compas_cem import JSON_DATA
from compas_cem import TEMP

from compas_cem.diagrams import FormDiagram

from compas_cem.loads import NodeLoad

from compas_cem.plotters import FormPlotter
from compas_cem.plotters import TopologyPlotter

from compas_cem.equilibrium import force_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import PointGoal
from compas_cem.optimization import PlaneGoal

from compas_cem.optimization import TrailEdgeConstraint
from compas_cem.optimization import DeviationEdgeConstraint

from compas.geometry import Plane
from compas.geometry import length_vector

# ------------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------------

IN = os.path.abspath(os.path.join(JSON_DATA, "w1_cem_2d_bridge_rhino.json"))

optimize = True
plot = True
view = False
save_fig = True

# ------------------------------------------------------------------------------
# Form Diagram
# ------------------------------------------------------------------------------

form = FormDiagram.from_json(IN)

# ------------------------------------------------------------------------------
# Store initial lines
# ------------------------------------------------------------------------------

keys = list(form.deviation_edges())
deviation_force = 1.0
form.edges_attribute(name="force", value=deviation_force, keys=keys)

load = [-1.0, 0.0, 0.0]
for node in form.root_nodes():
    form.add_load(NodeLoad(node, load))

# ------------------------------------------------------------------------------
# Collect Trails and Edge lines
# ------------------------------------------------------------------------------

tr = form.trails()
edge_lines = [form.edge_coordinates(*edge) for edge in form.edges()]

# ------------------------------------------------------------------------------
# Initialize optimizer
# ------------------------------------------------------------------------------

optimizer = Optimizer()

# ------------------------------------------------------------------------------
# Define goals / Targets
# ------------------------------------------------------------------------------

optimizer.add_goal(PointGoal(node=3, point=[29.13,22.20,0.00]))
optimizer.add_goal(PointGoal(node=7, point=[42.99,-14.17,0.00]))

# ------------------------------------------------------------------------------
# Define optimization parameters / constraints
# ------------------------------------------------------------------------------

bound_t = 20.0
bound_d = 20.0

for edge in form.trail_edges():
    optimizer.add_constraint(TrailEdgeConstraint(edge, bound_t, bound_t))

for edge in form.deviation_edges():
    optimizer.add_constraint(DeviationEdgeConstraint(edge, bound_d, bound_d))

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

if optimize:
    # record starting time
    start = time()

    # optimization constants
    opt_algorithm = "LD_LBFGS"  # LN_BOBYQA / LD_LBFGS / LD_SLSQP
    # opt_algorithm = "LN_BOBYQA"

    iters = 1000  # 100

    stopval = 1e-6 # 1e-4

    ftol = None  # 1e-3

    step_size = 1e-3  # 1e-6


    # optimize
    x_opt, l_opt = optimizer.solve_nlopt(form=form,
                                         algorithm=opt_algorithm,
                                         iters=iters,
                                         step_size=step_size,
                                         stopval=stopval,
                                         ftol=ftol,
                                         mode="autodiff",
                                         verbose=False)

   # print out results
    print("Form. # Nodes: {}, # Edges: {}".format(form.number_of_nodes(),
                                                  form.number_of_edges()))
    print("Optimizer. # Variables {}, # Goals {}".format(optimizer.number_of_constraints(),
                                                         optimizer.number_of_goals()))
    print("Elapsed time: {}".format(time() - start))
    print("Total error: {}".format(l_opt))

# ------------------------------------------------------------------------------
# Print put residual forces at supports (a.k.a reaction forces)
# ------------------------------------------------------------------------------

    for node in form.support_nodes():
        residual = form.node_residual(node)
        print("node: {} reaction force: {}".format(node, residual))

# ------------------------------------------------------------------------------
# Plotter
# ------------------------------------------------------------------------------

if plot:
    plotter = FormPlotter(form, figsize=(16, 9))

    plotter.draw_nodes(radius=0.30)
    plotter.draw_edges()
    plotter.draw_loads(scale=2.0, gap=0.75)
    plotter.draw_residuals(scale=2.0, gap=0.75)
    # plotter.draw_segments(edge_lines)

    points = []
    for key, goal in optimizer.goals.items():
        if not isinstance(goal, PointGoal):
            continue
        pt = goal.target()
        points.append({
            "pos": pt[:2],
            "radius": 0.5,
            "facecolor": (255, 153, 0)
        })

    # plotter.draw_points(points)

    if save_fig:
        path = os.path.abspath(os.path.join(TEMP, "iass_2021/mini_bridge"))
        plt.autoscale()
        plt.tight_layout()
        plt.savefig(path, bbox_inches='tight', pad_inches=0)

    plotter.show()
