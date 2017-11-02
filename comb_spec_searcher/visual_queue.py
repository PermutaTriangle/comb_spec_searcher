from threading import RLock  # I don't know if mpl uses threading, but lets hope for the best
from collections import deque, defaultdict

import enum

import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
from matplotlib.lines import Line2D
import matplotlib.patheffects as path_effects
from matplotlib.textpath import TextPath

from tpt_base.misc.colors import Solarized
from tpt_base.algs.tree_drawing import walker
from tpt_base.data_structures.graphs import AbstractOrderedTree


# A class that allows for zooming and panning with mouse
# A combination of answers from:
# https://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel


class ZoomPan:
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None

    def zoom_factory(self, ax, base_scale = 2.):
        def zoom(event):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location

            if event.button == 'down':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'up':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print(event.button)

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

            ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
            ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])
            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest
        fig.canvas.mpl_connect('scroll_event', zoom)

        return zoom

    def pan_factory(self, ax):
        def onPress(event):
            if event.inaxes != ax: return
            self.cur_xlim = ax.get_xlim()
            self.cur_ylim = ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.xpress, self.ypress = self.press

        def onRelease(event):
            self.press = None
            ax.figure.canvas.draw()

        def onMotion(event):
            if self.press is None: return
            if event.inaxes != ax: return
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            ax.set_xlim(self.cur_xlim)
            ax.set_ylim(self.cur_ylim)

            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest

        # attach the call back
        fig.canvas.mpl_connect('button_press_event',onPress)
        fig.canvas.mpl_connect('button_release_event',onRelease)
        fig.canvas.mpl_connect('motion_notify_event',onMotion)

        #return the function
        return onMotion


DEBUG = False
LIGHT = True
AUTOSCALE = True



def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


NODE_RADIUS = .2
LEVEL_DIFF = 1
LINE_WIDTH = 3


class Color:
    NORMAL = Solarized.violet
    VERIFIED = Solarized.green
    #PICKABLE = Solarized.blue
    EQUIVALENCE = Solarized.base1 if LIGHT else Solarized.base01
    SUM = Solarized.blue
    PRODUCT = Solarized.cyan
    BACKGROUND = Solarized.base3 if LIGHT else Solarized.base03
    EDGE = Solarized.base1 if LIGHT else Solarized.base01
    EMPH = Solarized.yellow


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


class VisNode:
    pass


class ObjNode(mpatches.Circle, VisNode):
    def __init__(self, center, raw_tree, *args, **kwargs):
        self.original_color = None
        super().__init__(center, NODE_RADIUS, *args, **kwargs)
        self.raw_tree = raw_tree

    def set_facecolor(self, color):
        super().set_facecolor(color)
        if self.original_color is None:
            self.original_color = color


class CtrlNode(mpatches.Rectangle, VisNode):
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
            zorder=-100,
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
            identifier=None,
        ):
        self.label = label

        self.children = children

        self.data = set() if data is None else data

        self.get_description = description_getter

        self.patch = None

        self.identifier = identifier


# The Queue class itself, used in the tilescope to present the next label needing work


class VisualQueue:
    def __init__(self, tilescope):
        self.tilescope = tilescope
        self.queue = deque()
        self.last_hover = None
        self.lock = RLock()
        self.expanded = set()  # List of obj node labels that have been passed to tree
        self.show_children = set()  # List of node identifiers that has been clicked on (alternates to off)
        self.nodes = set()
        self.obj_nodes = set()
        self.done = False  # True iff currently just displaying non-interactive proof tree
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
        self.ax = ax
        self.zp = ZoomPan()
        self.zp.zoom_factory(self.ax, 1.1)
        self.zp.pan_factory(self.ax)
        self.redraw_tree()
        # Register redrawing function with tilescope
        self.tilescope.post_expand_objects_functions.append((self.redraw_tree, [], {}))
        # Make plot interactive and show it
        plt.interactive(True)
        plt.show()

    def hover_event_handler(self, event):
        with self.lock:
            found_patch = False
            for patch in self.nodes:
                if patch.contains(event)[0]:
                    if self.last_hover is None or patch.raw_tree.label != self.last_hover.raw_tree.label:
                        found_patch = True
                        self.last_hover = patch
                        print()
                        print("HOVERING OVER:")
                        print()
                        print(patch.raw_tree.get_description())
                        print()
                    break
            if found_patch:
                patch = self.last_hover
                if isinstance(patch, ObjNode):
                    # TODO: Do more efficiently
                    for obj_node in self.obj_nodes:
                        if obj_node.raw_tree.label == patch.raw_tree.label:
                            obj_node.set_radius(obj_node.radius + .05)
                            obj_node.set_facecolor(Color.EMPH)
                        else:
                            obj_node.set_radius(NODE_RADIUS)
                            obj_node.set_facecolor(obj_node.original_color)

    def pick_event_handler(self, event):
        if event.mouseevent.button != 1 or self.done:
            # We only care about clicking on the nodes
            return
        with self.lock:
            if isinstance(event.artist, VisNode):
                if isinstance(event.artist, CtrlNode):
                    if Flag.PHANTOM in event.artist.raw_tree.data:
                        debug_print("+++ Phantom node clicked")
                        return  # TODO: Is it more natural to click these?
                    identifier = event.artist.raw_tree.identifier
                    if identifier in self.show_children:
                        debug_print("+++ Remove id from show children ids:", identifier)
                        self.show_children.remove(identifier)
                    else:
                        debug_print("+++ Add id to show children ids:", identifier)
                        self.show_children.add(identifier)
                    self.redraw_tree()
                elif isinstance(event.artist, ObjNode):
                    if Flag.VERIFIED in event.artist.raw_tree.data:
                        debug_print("+++ Ignore click because node is verified obj node")
                        return
                    label = event.artist.raw_tree.label
                    if label in self.show_children:
                        debug_print("+++ Remove label from show children labels:", label)
                        self.show_children.remove(label)
                        # Has already been expanded
                        self.redraw_tree()
                    else:
                        debug_print("+++ Add label to show children labels:", label)
                        self.show_children.add(label)
                        if label in self.expanded:
                            self.redraw_tree()
                        else:
                            self.expanded.add(label)
                            self.queue.append(event.artist.raw_tree.label)
            else:
                raise RuntimeError("Unexpected non-node picker:", event.artist)

    def draw_proof_tree_instead(self, proof_tree):
        # Construct raw tree from proof_tree
        raw_tree_root = RawTree(self.tilescope.start_label, children=[])
        frontier = deque()
        frontier.append((raw_tree_root, proof_tree.root))
        while frontier:
            raw_tree, proof_tree = frontier.popleft()
            raw_tree.data.add(Flag.OBJECT)
            raw_tree.data.add(Flag.VERIFIED)
            raw_tree.get_description = lambda rt=raw_tree: str(self.tilescope.objectdb.get_object(rt.label))
            branch_labels = tuple(self.tilescope.objectdb.get_label(child.in_tiling)
                                  for child in proof_tree.children)

            debug_print("+++ Proof tree rooted at", raw_tree.label)
            if not proof_tree.children and not proof_tree.strategy_verified:
                debug_print("+++ Possible need to resolve recursion")

            out_label = self.tilescope.objectdb.get_label(proof_tree.out_tiling)

            if raw_tree.label != out_label:
                debug_print("+++ Adding intermediate eqv ctrl node from", raw_tree.label, "to", out_label)
                # Need eqv node between
                eqv_ctrl_raw_tree = RawTree(children=[])
                eqv_ctrl_raw_tree.data.add(Flag.CONTROL)
                eqv_ctrl_raw_tree.data.add(Flag.EQUIVALENCE)
                eqv_ctrl_raw_tree.get_description = lambda l=raw_tree.label, el=out_label: \
                    self.tilescope.equivdb.get_explanation(l, el)
                eqv_obj_raw_tree = RawTree(out_label, children=[])
                eqv_ctrl_raw_tree.children.append(eqv_obj_raw_tree)
                raw_tree.children.append(eqv_ctrl_raw_tree)
                frontier.appendleft((eqv_obj_raw_tree, proof_tree))
            else:
                # No eqv node needed, just branch
                if not proof_tree.children:
                    continue
                branch_ctrl_raw_tree = RawTree(children=[])
                raw_tree.children.append(branch_ctrl_raw_tree)
                branch_ctrl_raw_tree.get_description = lambda pt=proof_tree: pt.formal_step
                branch_ctrl_raw_tree.data.add(Flag.CONTROL)
                def is_product(bls):
                    return raw_tree.label in self.tilescope.ruledb.back_maps \
                       and bls in self.tilescope.ruledb.back_maps[raw_tree.label]
                branch_ctrl_raw_tree.data.add(
                    Flag.PRODUCT
                    if is_product(branch_labels)
                    else
                    Flag.SUM
                )
                for sub_proof_tree in proof_tree.children:
                    branch_obj_raw_tree = RawTree(
                        self.tilescope.objectdb.get_label(sub_proof_tree.in_tiling),
                        children=[]
                    )
                    branch_ctrl_raw_tree.children.append(branch_obj_raw_tree)
                    frontier.append((branch_obj_raw_tree, sub_proof_tree))

        draw_tree_root = walker(raw_tree_root)

        self.draw_to_mpl(draw_tree_root, raw_tree_root)

    def redraw_tree(self):
        debug_print("+++ Waiting on lock to redraw")
        with self.lock:
            debug_print("+++ Acquired lock to redraw")
            proof_tree = self.tilescope.get_proof_tree() if len(self.tilescope.objectdb.label_to_info) > 1 else None
            if proof_tree is not None:
                self.done = True
                debug_print("+++ A tree has been found!")
                debug_print(type(proof_tree))
                debug_print(proof_tree)
                self.draw_proof_tree_instead(proof_tree)
                return
            else:
                debug_print("+++ A tree has yet to be found...")

            # Construct draw-able tree from tilescope data

            start_label = self.tilescope.start_label
            raw_tree_root = RawTree(start_label)
            if not self.tilescope.is_expanded(start_label):
                debug_print("+++ Start label", start_label, "is not expanded")
                raw_tree_root.data.add(Flag.EXPANDABLE)

            debug_print("+++ Gathering information for raw_tree")

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
                elif raw_tree.label not in self.show_children:
                    debug_print("+++ User doesn't want its child ctrl nodes displayed")
                else:
                    def is_product(bls):
                        return raw_tree.label in self.tilescope.ruledb.back_maps \
                           and bls in self.tilescope.ruledb.back_maps[raw_tree.label]
                    # Add branching things
                    for branch_labels in sorted(self.tilescope.ruledb.rules_dict[raw_tree.label],
                                                key=lambda bls: (1 if is_product(bls) else 0, bls)):
                        debug_print("+++ It branches to", branch_labels)
                        branch_ctrl_identifier = (raw_tree.label, branch_labels)
                        branch_ctrl_raw_tree = RawTree(children=[], identifier=branch_ctrl_identifier)
                        branch_ctrl_raw_tree.data.add(Flag.CONTROL)
                        branch_ctrl_raw_tree.data.add(
                            Flag.PRODUCT
                            if is_product(branch_labels)
                            else
                            Flag.SUM
                        )
                        branch_ctrl_raw_tree.get_description = lambda l=raw_tree.label, \
                                                                     ls=branch_labels: \
                            self.tilescope.ruledb.explanation(l, ls)
                        if branch_ctrl_identifier in self.show_children:
                            # Add children
                            for branch_label in branch_labels:
                                branch_obj_raw_tree = RawTree(branch_label)
                                branch_ctrl_raw_tree.children.append(branch_obj_raw_tree)
                                frontier.append(branch_obj_raw_tree)
                        raw_tree.children.append(branch_ctrl_raw_tree)

                    # Add equivalent things to tree and frontier
                    if any(eqv_label in seen for eqv_label in self.tilescope.equivdb.equivalent_set(raw_tree.label)):
                        # Don't draw any equivalent branching if it has been done for some equivalent node
                        continue
                    # Mark as seen, all later-found nodes for same label will be phantoms
                    seen.add(raw_tree.label)
                    for eqv_label in sorted(self.tilescope.equivdb.equivalent_set(raw_tree.label)):
                        if eqv_label == raw_tree.label:
                            debug_print("+++ Ignoring itself in eqv draw")
                            continue
                        debug_print("+++ It has an eqv node label of", eqv_label)
                        eqv_ctrl_identifier = (raw_tree.label, 0, eqv_label)
                        eqv_ctrl_raw_tree = RawTree(identifier=eqv_ctrl_identifier)
                        eqv_ctrl_raw_tree.data.add(Flag.CONTROL)
                        eqv_ctrl_raw_tree.data.add(Flag.EQUIVALENCE)
                        eqv_ctrl_raw_tree.get_description = lambda l=raw_tree.label, el=eqv_label: \
                            self.tilescope.equivdb.get_explanation(l, el)
                        if eqv_ctrl_identifier in self.show_children:
                            eqv_obj_raw_tree = RawTree(eqv_label)
                            eqv_obj_raw_tree.data.add(Flag.EQUIVALENCE)
                            frontier.append(eqv_obj_raw_tree)
                            eqv_ctrl_raw_tree.children = (eqv_obj_raw_tree,)
                        raw_tree.children.append(eqv_ctrl_raw_tree)

            # Use algorithms to determine x and y positions; its DrawTree

            draw_tree_root = walker(raw_tree_root)

            #debug_print()
            #debug_print("+++ DRAWTREE")
            #debug_print("+++", draw_tree_root)
            #debug_print("+++ RAWTREE ROOT DATA")
            #debug_print("+++", raw_tree_root.data)
            #debug_print()
            self.draw_to_mpl(draw_tree_root, raw_tree_root)

    def draw_to_mpl(self, draw_tree_root, raw_tree_root):
        # Use the computed coordinates to do plot the raw data
        self.nodes = set()
        self.obj_nodes = set()
        self.ax.cla()  # Clear axes

        frontier = deque()
        debug_print()
        debug_print("+++ Drawing tree!")
        debug_print()
        frontier.append((raw_tree_root, draw_tree_root, None))
        while frontier:
            raw_tree, draw_tree, parent_xy = frontier.popleft()
            data = raw_tree.data
            xy = (float(draw_tree.x), -float(draw_tree.y))
            x, y = xy
            debug_print("+++ Drawing:")
            debug_print("+++    ", raw_tree)
            debug_print("+++    ", raw_tree.data)
            debug_print("+++    ", xy)
            if parent_xy is not None:
                # TODO: Different lines for different types of nodes
                self.ax.add_line(TreeLine(
                    parent_xy,
                    xy,
                    linestyle=":" if Flag.PHANTOM in data else "solid",
                ))
            if Flag.OBJECT in data:
                # Node is an object node
                node = ObjNode(xy, raw_tree)
#                if Flag.EXPANDABLE in data:
#                    # Change color to notify of expandability
#                    node.set_color(Color.PICKABLE)
                if Flag.VERIFIED in data:
                    node.set_color(Color.VERIFIED)
                else:
                    node.set_color(Color.NORMAL)
            elif Flag.CONTROL in data:
                node = CtrlNode(xy, raw_tree)
                if Flag.EQUIVALENCE in data:
                    node.set_color(Color.EQUIVALENCE)
                    text_content = "="
                elif Flag.PRODUCT in data:
                    node.set_color(Color.PRODUCT)
                    text_content = "x"
                elif Flag.SUM in data:
                    node.set_color(Color.SUM)
                    text_content = "+"
                else:
                    raise RuntimeError("Unknown control node type for drawing")
                # Make text on top of it
                text_path = TextPath(
                    (x - (.09 if text_content == "x" else .125), y-.09),
                    text_content,
                    size=.3,
                )
                for a in text_path.to_polygons():
                    p = mpatches.Polygon(a, fill=True, color="white", zorder=100)
                    self.ax.add_patch(p)
            else:
                raise RuntimeError("Unknown node type for drawing")

            debug_print()

            node.set_picker(True)
            self.ax.add_patch(node)
            self.nodes.add(node)
            if Flag.OBJECT in raw_tree.data:
                self.obj_nodes.add(node)

            # Add children to drawing frontier as well
            frontier.extend((child_raw, child_draw, xy)
                            for child_raw, child_draw
                            in zip(raw_tree.children, draw_tree.children))

        # Redraw and scale viewport if needed

        if AUTOSCALE:
            self.ax.autoscale()
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
