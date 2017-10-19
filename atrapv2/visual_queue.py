from threading import Lock  # I don't know if mpl uses threading, but lets hope for the best
from collections import deque, defaultdict

import enum

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
from matplotlib.lines import Line2D

from tpt_base.misc.colors import Solarized
from tpt_base.algs.tree_drawing import walker
from tpt_base.data_structures.graphs import AbstractOrderedTree


mpl.use("TkAgg")


NODE_WITH = .2
LEVEL_DIFF = 1
LINE_WIDTH = 4


class Color(enum.Enum):
    ROOT = Solarized.yellow
    VERIFIED = Solarized.green
    PICKABLE = Solarized.red
    EQUIVALENCE = Solarized.base1
    SUM = Solarized.blue
    PRODUCT = Solarized.cyan
    BACKGROUND = Solarized.base3
    EDGE = Solarized.base1


class Flag(enum.Enum):
    VERIFIED = enum.auto()
    PHANTOM = enum.auto()
    SUM = enum.auto()
    PRODUCT = enum.auto()
    EQUIVALENCE = enum.auto()
    ROOT = enum.auto()
    #DESCRIPTION = enum.auto()


# The classes for the things we will draw on the screen


class ObjNode(mpatches.Circle):
    def __init__(self, center, raw_node, *args, **kwargs):
        super().__init__(center, NODE_WITH, *args, **kwargs)
        self.raw_node = raw_node


class CtrlNode(mpatches.Rectangle):
    def __init__(self, center, raw_node, *args, **kwargs):
        bottom_left = tuple(x_or_y - NODE_WITH/2 for x_or_y in center)
        super().__init__(bottom_left, NODE_WITH, NODE_WITH, *args, **kwargs)
        self.raw_node = raw_node


class TreeLine(Line2D):
    def __init__(self, origin, end, *args, **kwargs):
        ox, oy = origin
        ex, ey = end
        super().__init__(
            (ox, ox, ex, ex),
            (oy - NODE_WITH, oy - LEVEL_DIFF, ey + LEVEL_DIFF, ey + NODE_WITH),
            *args,
            color=Color.EDGE,
            linewidth=LINE_WIDTH,
            **kwargs,
        )


# Data processing tree, representing the information of a metatree


class RawTree(AbstractOrderedTree):
    children = None
    def __init__(
            self,
            label=None,
            *,
            children=(),
            data=set(),
            description_getter=lambda raw_tree: "NO DESCRIPTION",
        ):
        self.label = label

        self.children = children

        self.data = data

        self.get_description = description_getter

        self.node = None


# The Queue class itself, used in the tilescope to present the next label needing work


class VisualQueue:
    def __init__(self, tilescope):
        self.tilescope = tilescope
        self.queue = deque()
        self.pickers = set()
        self.last_hover = None
        self.lock = Lock()
        # Create figure
        self.fig = plt.figure()
        # Register event handlers
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover_event_handler)
        self.fig.canvas.mpl_connect("pick_event", self.pick_event_handler)
        # Create axes
        ax = self.fig.add_subplot(
            111,
            aspect="equal",
            facecolor=Solarized.base3
        )
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.add_patch(mpatches.Circle((0, 0), 1, picker=True))
        ax.autoscale()  # Perhaps unnecessary
        self.ax = ax
        self.redraw_tree()
        # Register redrawing function with tilescope
        self.tilescope.post_expand_objects_functions.append((self.redraw_tree, [], {}))
        # Make plot interactive and show it
        plt.interactive(True)
        plt.show()

    def hover_event_handler(self, event):
        with self.lock:
            for patch in self.ax.patches:
                if patch.contains(event):
                    if patch != self.last_hover:
                        self.last_hover = patch
                        print(patch)
                    break

    def pick_event_handler(self, event):
        with self.lock:
            # Find the relevant tiling and pass it to the queue
            self.queue.append(0)

    def redraw_tree(self):
        with self.lock:

            # Construct draw-able tree from tilescope data

            start_label = self.tilescope.start_label
            raw_tree = RawTree(start_label, data=set([Flag.ROOT]))

            seen = set()
            frontier = deque()
            frontier.append(raw_tree)
            while frontier:
                node = frontier.popleft()
                # Add a description getter to the node
                node.get_description = lambda node: str(self.tilescope.objectdb.get_object(node.label))

                # If the node is verified, we draw it in a way that highlights that
                if self.tilescope.equivdb.is_verified(node.label):
                    node.data.add(Flag.VERIFIED)

                if node.label in seen:
                    # If the node has been seen before, it is a phantom
                    node.data.add(Flag.PHANTOM)
                    # We don't draw any of its children, so we're done
                else:
                    # Mark as seen, all later-found nodes for same label will be phantoms
                    seen.add(node.label)
                    # Add equivalent things to tree and frontier
                    for eqv_label in self.tilescope.equivdb.equivalent_set(node.label):
                        eqv_control_node = RawTree()
                        eqv_control_node.data.add(Flag.EQUIVALENCE)
                        eqv_control_node.get_description = lambda node, eqv_label=eqv_label: \
                            self.tilescope.equivdb.get_explanation(
                                node.label,
                                eqv_label,
                            )
                        eqv_node = RawTree(eqv_label)
                        eqv_node.data.add(Flag.EQUIVALENCE)
                        eqv_control_node.children = (eqv_node,)
                    # Add branching things
                    for branch_labels in self.tilescope.ruledb.rules_dict[start_label]:
                        branch_control_node = RawTree(children=[])
                        branch_control_node.data.add(Flag.SUM)  # TODO: How to separate product and sum?
                        branch_control_node.get_description = lambda node, \
                                                                     branch_labels=branch_labels: \
                            self.tilescope.ruledb.explanantion(
                                node.label,
                                branch_labels,
                            )
                        for branch_label in branch_labels:
                            branch_node = RawTree(branch_label)
                            branch_control_node.children.append(branch_node)
                            frontier.append(branch_node)

            # Use algorithms to determine x and y positions; its DrawTree

            draw_tree = walker(raw_tree)

            # Use the computed coordinates to do construct the tree

            # TODO: Do things

            self.pickers = set()

            print("We got this draw tree:")
            print(draw_tree)

            # Redraw and scale viewport if needed

            #self.ax.autoscale()  # TODO: Will commenting this suffice to keep viewport?
            self.fig.canvas.draw()

    def next(self):
        while not self.queue:
            plt.pause(.1)
        return self.queue.popleft()

    def do_level(self):
        raise NotImplementedError("Use a cap of 1 with your auto search, never call do_level")

    def add_to_working(self, label):
        pass  # Ignore

    def add_to_next(self, label):
        pass  # Ignore

    def add_to_curr(self, label):
        pass  # Ignore
