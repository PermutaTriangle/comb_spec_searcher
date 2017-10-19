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


DEBUG = True


def debug_print(*args, **kwargs):
    print(*args, **kwargs)


NODE_RADIUS = .2
LEVEL_DIFF = 1
LINE_WIDTH = 4


class Color:
    NORMAL = Solarized.yellow
    VERIFIED = Solarized.green
    PICKABLE = Solarized.red
    EQUIVALENCE = Solarized.base1
    SUM = Solarized.blue
    PRODUCT = Solarized.cyan
    BACKGROUND = Solarized.base3
    EDGE = Solarized.base1


class Flag(enum.Enum):
    # What kind of node
    CONTROL = enum.auto()
    OBJECT = enum.auto()

    # Object node details
    VERIFIED = enum.auto()
    PHANTOM = enum.auto()
    EXPANDABLE = enum.auto()

    # Types of branching
    EQUIVALENCE = enum.auto()
    SUM = enum.auto()
    PRODUCT = enum.auto()


# The classes for the things we will draw on the screen


class ObjNode(mpatches.Circle):
    def __init__(self, center, raw_tree, *args, **kwargs):
        super().__init__(center, NODE_RADIUS, *args, **kwargs)
        self.raw_tree = raw_tree


class CtrlNode(mpatches.Rectangle):
    def __init__(self, center, raw_tree, *args, **kwargs):
        bottom_left = tuple(x_or_y - NODE_RADIUS for x_or_y in center)
        super().__init__(bottom_left, 2*NODE_RADIUS, 2*NODE_RADIUS, *args, **kwargs)
        self.raw_tree = raw_tree


class TreeLine(Line2D):
    def __init__(self, origin, end, *args, **kwargs):
        ox, oy = origin
        ex, ey = end
        super().__init__(
            (ox, ox, ex, ex),
            (oy - NODE_RADIUS, oy - LEVEL_DIFF/2, ey + LEVEL_DIFF/2, ey + NODE_RADIUS),
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
            data=None,
            description_getter=lambda raw_tree: "NO DESCRIPTION",
        ):
        self.label = label

        self.children = children

        self.data = set() if data is None else data

        self.get_description = description_getter

        self.patch = None


# The Queue class itself, used in the tilescope to present the next label needing work


class VisualQueue:
    def __init__(self, tilescope):
        self.tilescope = tilescope
        self.queue = deque()
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
            facecolor=Color.BACKGROUND
        )
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        for spine in ax.spines.values():
            spine.set_visible(False)
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
                if patch.contains(event)[0] and patch != self.last_hover:
                    self.last_hover = patch
                    print()
                    print("HOVERING OVER:")
                    print()
                    print(patch.raw_tree.get_description())
                    print()
                    break

    def pick_event_handler(self, event):
        with self.lock:
            self.queue.append(event.artist.raw_tree.label)

    def redraw_tree(self):
        debug_print("+++ Waiting on lock to redraw")
        with self.lock:
            debug_print("+++ Acquired lock to redraw")

            self.ax.cla()  # Clear axes

            # Construct draw-able tree from tilescope data

            start_label = self.tilescope.start_label
            raw_tree_root = RawTree(start_label)
            if not self.tilescope.is_expanded(start_label):
                debug_print("+++ Start label", start_label, "is not expanded")
                raw_tree_root.data.add(Flag.EXPANDABLE)

            debug_print("+++ Gathering information for raw_tree")
            debug_print("+++ BEFORE We have a rules dict:")
            for item in self.tilescope.ruledb.rules_dict.items():
                debug_print("+++    ", item)

            seen = set()
            frontier = deque()
            frontier.append(raw_tree_root)
            while frontier:
                raw_tree = frontier.popleft()
                raw_tree.data.add(Flag.OBJECT)
                raw_tree.children = []
                debug_print("+++ Looking at subtree labeled", raw_tree.label)
                # Add a description getter to the node
                raw_tree.get_description = lambda rt=raw_tree: str(self.tilescope.objectdb.get_object(rt.label))

                if self.tilescope.equivdb.is_verified(raw_tree.label):
                    debug_print("+++ It is verified")
                    # If the raw_tree is verified, we draw it in a way that highlights that
                    raw_tree.data.add(Flag.VERIFIED)
                elif not self.tilescope.is_expanded(raw_tree.label):
                    # However, if it is not expanded, then we highlight that
                    debug_print("+++ It is expandable")
                    raw_tree.data.add(Flag.EXPANDABLE)

                if raw_tree.label in seen:
                    # If the raw_tree has been seen before, it is a phantom
                    debug_print("+++ It has been seen before")
                    raw_tree.data.add(Flag.PHANTOM)
                    # We don't draw any of its children, so we're done
                else:
                    # Add branching things
                    for branch_labels in self.tilescope.ruledb.rules_dict[raw_tree.label]:
                        debug_print("+++ It branches to", branch_labels)
                        branch_control_node = RawTree(children=[])
                        branch_control_node.data.add(Flag.CONTROL)
                        branch_control_node.data.add(
                            Flag.PRODUCT
                            if (raw_tree.label, branch_labels) in self.tilescope.ruledb.back_maps else
                            Flag.SUM
                        )
                        branch_control_node.get_description = lambda l=raw_tree.label, \
                                                                     ls=branch_labels: \
                            self.tilescope.ruledb.explanation(l, ls)
                        for branch_label in branch_labels:
                            branch_node = RawTree(branch_label)
                            branch_control_node.children.append(branch_node)
                            frontier.append(branch_node)
                        raw_tree.children.append(branch_control_node)
                    # Add equivalent things to tree and frontier
                    if any(eqv_label in seen for eqv_label in self.tilescope.equivdb.equivalent_set(raw_tree.label)):
                        continue
                    # Mark as seen, all later-found nodes for same label will be phantoms
                    seen.add(raw_tree.label)
                    for eqv_label in self.tilescope.equivdb.equivalent_set(raw_tree.label):
                        if eqv_label == raw_tree.label:
                            debug_print("+++ Ignoring itself in eqv draw")
                            continue
                        debug_print("+++ It has an eqv node label of", eqv_label)
                        eqv_ctrl_raw_tree = RawTree()
                        eqv_ctrl_raw_tree.data.add(Flag.CONTROL)
                        eqv_ctrl_raw_tree.data.add(Flag.EQUIVALENCE)
                        eqv_ctrl_raw_tree.get_description = lambda l=raw_tree.label, el=eqv_label: \
                            self.tilescope.equivdb.get_explanation(l, el)
                        eqv_obj_raw_tree = RawTree(eqv_label)
                        eqv_obj_raw_tree.data.add(Flag.EQUIVALENCE)
                        frontier.append(eqv_obj_raw_tree)
                        eqv_ctrl_raw_tree.children = (eqv_obj_raw_tree,)
                        raw_tree.children.append(eqv_ctrl_raw_tree)

            debug_print("+++ AFTER We have a rules dict:")
            for item in self.tilescope.ruledb.rules_dict.items():
                debug_print("+++    ", item)

            # Use algorithms to determine x and y positions; its DrawTree

            draw_tree_root = walker(raw_tree_root)

            # Use the computed coordinates to do plot the raw data

            debug_print()
            debug_print("+++ DRAWTREE")
            debug_print("+++", draw_tree_root)
            debug_print("+++ RAWTREE ROOT DATA")
            debug_print("+++", raw_tree_root.data)
            debug_print()

            debug_print("+++ Drawing tree!")
            debug_print()
            frontier.append((raw_tree_root, draw_tree_root, None))
            while frontier:
                raw_tree, draw_tree, parent_xy = frontier.popleft()
                data = raw_tree.data
                xy = (float(draw_tree.x), -float(draw_tree.y))
                debug_print("+++ Drawing:")
                debug_print("+++    ", raw_tree)
                debug_print("+++    ", raw_tree.data)
                debug_print("+++    ", xy)
                if parent_xy is not None:
                    # TODO: Different lines for different types of nodes
                    self.ax.add_line(TreeLine(parent_xy, xy))

                if Flag.OBJECT in data:
                    # Node is an object node
                    node = ObjNode(xy, raw_tree)
                    if Flag.EXPANDABLE in data:
                        # Node is a picker, can be clicked to expand
                        node.set_picker(True)
                        # Change color to notify of expandability
                        node.set_color(Color.PICKABLE)
                    elif Flag.VERIFIED in data:
                        node.set_color(Color.VERIFIED)
                    else:
                        node.set_color(Color.NORMAL)
                elif Flag.CONTROL in data:
                    node = CtrlNode(xy, raw_tree)
                    if Flag.EQUIVALENCE in data:
                        node.set_color(Color.EQUIVALENCE)
                    elif Flag.PRODUCT in data:
                        node.set_color(Color.PRODUCT)
                    elif Flag.SUM in data:
                        node.set_color(Color.SUM)
                    else:
                        raise RuntimeError("Unknown control node type for drawing")
                else:
                    raise RuntimeError("Unknown node type for drawing")

                debug_print()

                self.ax.add_patch(node)

                # Add children to drawing frontier as well
                frontier.extend((child_raw, child_draw, xy)
                                for child_raw, child_draw
                                in zip(raw_tree.children, draw_tree.children))

            # Redraw and scale viewport if needed

            self.ax.autoscale()  # TODO: Will commenting this suffice to keep viewport?
            self.fig.canvas.draw()

    def next(self):
        while not self.queue:
            plt.pause(.1)
        label = self.queue.popleft()
        debug_print("+++ Giving label", label, "to searcher")
        return label

    def do_level(self):
        raise NotImplementedError("Use a cap of 1 with your auto search, never call do_level")

    def add_to_working(self, label):
        pass  # Ignore

    def add_to_next(self, label):
        pass  # Ignore

    def add_to_curr(self, label):
        pass  # Ignore
