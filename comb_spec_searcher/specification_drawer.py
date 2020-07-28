"""
A specification drawer is for visualizing combinatorial specification object
"""
import json
import os
import tempfile
import threading
import time
import uuid
import webbrowser
from copy import copy
from typing import TYPE_CHECKING, ClassVar, Dict, List, Tuple

from logzero import logger
from typing_extensions import TypedDict

from .combinatorial_class import CombinatorialClass
from .strategies import EquivalencePathRule, Rule, VerificationRule

if TYPE_CHECKING:
    from .specification import CombinatorialSpecification

__all__ = ("SpecificationDrawer", "ForestSpecificationDrawer")


class TreantNode(TypedDict):
    innerHTML: str
    collapsable: bool
    collapsed: bool
    children: list


class TreantConfig(TypedDict):
    chart: dict
    nodeStructure: TreantNode
    tooltips: List[Dict[str, str]]


class SpecificationDrawer:
    """
    A specification drawer is for visualizing CombinatorialSpecification by making
    HTML file that contains an interactive tree using the Treant javascript library

    https://fperucic.github.io/treant-js/
    Treant library converts a json of TreantNodes to HTML code
    """

    def __init__(
        self,
        spec: "CombinatorialSpecification",
        levels_shown: int = 0,
        levels_expand: int = 0,
    ):
        """
        Initialise SpecificationDrawer.

        OTHER INPUT:
            - 'levels_shown': number of levels displayed at the start.
            If 0 then the whole tree is displayed
            - 'levels_expand': number of levels displayed after expanding a node.
            If 0 then the rest of the tree is displayed
        """
        self.spec = spec
        self.tooltips: List[Dict[str, str]] = []
        self._rules_dict_copy = copy(spec.rules_dict)
        self.levels_shown = levels_shown
        self.levels_expand = levels_expand
        self.tree = self._to_tree(spec.root)

    @staticmethod
    def _get_new_node_id() -> str:
        new_id = uuid.uuid1()
        return str(new_id)

    def _to_tree(
        self, comb_class: CombinatorialClass, rec_depth: int = 0
    ) -> TreantNode:
        """Create the subtree rooted in comb_class"""
        try:
            # checks if the rule has come before
            rule = self._rules_dict_copy.pop(comb_class)
            recursed = False
        except KeyError:
            # recursion
            rule = self.spec.get_rule(comb_class)
            recursed = True
        if isinstance(rule, EquivalencePathRule):
            child = rule.children[0]
            try:
                rule = self._rules_dict_copy.pop(child)
            except KeyError:
                # rule has recurred before
                rule = self.spec.get_rule(child)
                recursed = True
            comb_classes = [comb_class, child]
        else:
            comb_classes = [comb_class]
        html_node = self.comb_classes_to_html_node(comb_classes)
        treant_node, node_id = self._create_standard_node(html_node)
        self._create_standard_tooltip(comb_classes, node_id)
        if recursed:
            children = []
        else:
            children = [self._to_tree(child, rec_depth + 1) for child in rule.children]

        # If a node has children we create a delimiter node between them
        # in order to separate tooltip describing the steps taking in the tree

        if children and isinstance(rule, Rule):
            delimiter_node, node_id = self._create_delimiter_node(
                rule, children, rec_depth
            )
            self._create_delimiter_tooltip(rule, node_id)
            children = [delimiter_node]

        treant_node["children"] = children
        return treant_node

    def _create_delimiter_tooltip(self, rule: Rule, node_identifier: str) -> None:
        """Creates hover over tooltip for delimiter node"""
        tooltip = {
            "content": f"<p>Formal step:<br/>{rule.formal_step}</p>",
            "selector": f"#node{node_identifier}",
        }
        self.tooltips.append(tooltip)

    def _create_standard_tooltip(
        self, comb_classes: List[CombinatorialClass], node_identifier: str
    ) -> None:
        """Creates hover over tooltip for standard node"""
        rule = self.spec.get_rule(comb_classes[0])
        if isinstance(rule, EquivalencePathRule):
            # need to use the rule to be able to see the whole eqv path
            rule_string = str(rule).replace("\n", "<br>")
            # get the rule that starts from the end of the equiv path
            rule = self.spec.get_rule(comb_classes[-1])
        else:
            rule_string = str(comb_classes[0]).replace("\n", "<br>")
        labels = [str(self.spec.get_label(comb_class)) for comb_class in comb_classes]
        labels_string = ", ".join(labels)
        tooltip = {
            "content": f"<p>Labels: {labels_string}</p><pre>{rule_string}</pre>",
            "selector": f"#node{node_identifier}",
        }
        if isinstance(rule, VerificationRule):
            tooltip["content"] += f"<p>Verified: {rule.formal_step}</p>"
        self.tooltips.append(tooltip)

    def _create_standard_node(self, html_node: str) -> Tuple[TreantNode, str]:
        """Returns a tuple containing a standard treant node and its id."""
        new_id = self._get_new_node_id()
        treant_node = TreantNode(
            innerHTML=f'<div id="node{new_id}" data-toggle="tooltip">{html_node}</div>',
            collapsable=False,
            collapsed=False,
            children=[],
        )
        return treant_node, new_id

    def _create_delimiter_node(
        self, rule: Rule, children: List[TreantNode], rec_depth: int
    ) -> Tuple[TreantNode, str]:
        """
        Returns tuple containing delimiter node that describesthe steps taken between
        the rules and the node id
        """
        new_id = self._get_new_node_id()
        symbol = rule.strategy.get_op_symbol()
        delimiter_html = f'<div class="and-gate" id={new_id}>{symbol}</div>'

        # collapses at levels_shown and at every levels_expand after that
        collapsed = rec_depth != 0 and (
            rec_depth == self.levels_shown
            or (  # collapse at every levels_expand after levels_shown
                self.levels_expand != 0  # if 0 we don't collapse
                and rec_depth >= self.levels_shown
                and (rec_depth + self.levels_expand) % self.levels_expand == 0
            )
        )
        delimiter_node = TreantNode(
            innerHTML=f"""<div id="node{new_id}"
                data-toggle="tooltip">{delimiter_html}</div>""",
            collapsable=True,
            collapsed=collapsed,
            children=children,
        )
        return delimiter_node, new_id

    def comb_classes_to_html_node(
        self,
        comb_classes: List[CombinatorialClass],
        additional_style: str = "",
        additional_label_style: str = "",
    ) -> str:
        """Returns a representation of comb classes as a single html node string"""
        if not comb_classes:
            raise RuntimeError("comb_classes argument should not be empty")
        html = ""
        inner_style = ""
        if isinstance(self.spec.get_rule(comb_classes[-1]), VerificationRule):
            additional_style += "border-color: Green; border-width: 3px;"
            additional_label_style += "background-color: #89d75d;"
        # Check if comb_class has html representation function
        try:
            nodes = [comb_class.to_html_representation() for comb_class in comb_classes]
        except NotImplementedError:
            nodes = [
                str(comb_class).replace("\n", "<br>") for comb_class in comb_classes
            ]
            if len(nodes) > 1:
                inner_style += "border: 1px solid;"

        for i, node_string in enumerate(nodes):
            if i == len(nodes) - 1:  # removes margin on last node
                html += f"""<div class=inner-node-content
                    style="margin-right:0;{inner_style}">{node_string}</div>"""
            else:
                html += f"""<div class=inner-node-content style="{inner_style}">
                    {node_string}</div>"""

        # add labels above the node
        labels = [str(self.spec.get_label(comb_class)) for comb_class in comb_classes]
        labels_string = ", ".join(labels)
        labels_html = f"""<div class=label
            style='{additional_style}{additional_label_style}'>{labels_string}</div>"""
        return f"""{labels_html}<div class=node-content
            style='max-width:{300 * len(nodes)}px; {additional_style}'>{html}</div>"""

    def show(self) -> None:
        """Displays the CombinatorialSpecification tree in the web browser"""
        fsd = ForestSpecificationDrawer([self])
        fsd.show()

    def to_html(self) -> str:
        """Returns a html string that contains the whole tree"""
        fsd = ForestSpecificationDrawer([self])
        return fsd.to_html()

    def export_html(self, file_name: str) -> None:
        """Creates a html file in current directory"""
        fsd = ForestSpecificationDrawer([self])
        fsd.export_html(file_name)

    def to_treant_json(self) -> str:
        """returns a json input for Treant library"""
        fsd = ForestSpecificationDrawer([self])
        return json.dumps(fsd.add_tree_config(0))


class ForestSpecificationDrawer:
    """
    ForestSpecificationDrawer is for drawing multiple SpecificationDrawer in
    one single HTML file by navigating them with tabs
    """

    def __init__(self, sd_list: List[SpecificationDrawer]):
        self.sd_list = sd_list

    def add_tree_config(self, sd_index: int) -> TreantConfig:
        """Returns the tree and tooltip as TreantConfig for treant library"""
        return TreantConfig(
            nodeStructure=self.sd_list[sd_index].tree,
            tooltips=self.sd_list[sd_index].tooltips,
            chart={
                "maxDepth": 10000,
                "container": f"#spec-tree{sd_index}",
                "connectors": {"type": "bCurve", "style": {}},
                "nodeAlign": "BOTTOM",
                "levelSeparation": 35,
                "siblingSeparation": 30,
                "connectorsSpeed ": 10,
                "animation": {"nodeSpeed": 400, "connectorsSpeed": 200},
                "callback": {
                    # can't send functions over so it
                    # is dealt with on javascript side
                    "onTreeLoaded": "",
                },
            },
        )

    @staticmethod
    def _read_file(filename: str) -> str:
        with open(filename, "r", encoding="UTF8") as f:
            return f.read()

    def _get_static_files(self) -> str:
        script_dir = os.path.dirname(__file__)
        # Path to static files
        psf = os.path.join(script_dir, "resources/static/")
        treant_stylesheet = self._read_file(os.path.join(psf, "css/treant.css"))
        spec_stylesheet = self._read_file(os.path.join(psf, "css/specification.css"))
        bootstrap_stylesheet = self._read_file(os.path.join(psf, "css/bootstrap.css"))

        jquery_min_script = self._read_file(os.path.join(psf, "js/jquery.min.js"))
        bootstrap_min_script = self._read_file(
            os.path.join(psf, "js/bootstrap.bundle.min.js")
        )
        treant_script = self._read_file(os.path.join(psf, "js/Treant.js"))
        raphael_script = self._read_file(os.path.join(psf, "js/raphael.js"))
        static_files = f"""<style>
        {bootstrap_stylesheet}
        {treant_stylesheet}
        {spec_stylesheet}
        </style>
        <script>{jquery_min_script}</script>
        <script>{bootstrap_min_script}</script>
        <script>{treant_script}</script>
        <script>{raphael_script}</script>"""
        return static_files

    def _get_tree_content(self) -> Tuple[str, str, str]:
        tabs = ""
        forest = ""
        forest_input = []
        for i in range(len(self.sd_list)):
            tabs += f"""
            <li class='nav-item'>
                <a data-toggle="tab" id='spectab{i}' href='#spectabcontent{i}'
                    class="nav-link {"active" if i == 0 else ""}"
                    contenteditable="true">
                Spec {i}
                </a>
            </li>
            """
            forest += f"""
            <div id=spectabcontent{i}
                class='tab-pane {"active show" if i == 0 else ""}'>
                <div id="spec-tree{i}" class="Treant Treant-loaded"></div>
            </div>
            """
            forest_input.append(self.add_tree_config(i))
        json_input = json.dumps(forest_input)
        return (tabs, forest, json_input)

    def to_html(self) -> str:
        """Returns a html string that contains the whole forest"""
        static_files = self._get_static_files()
        tabs, forest, json_input = self._get_tree_content()

        html_string = f"""
        <!DOCTYPE html><html><head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>Specification</title>
        {static_files}
        <div>
            <ul class="nav nav-tabs">
                {tabs}
            </ul>

            <div class='tab-content mt-2'>
                {forest}
            </div>
        </div>
        <script>
        function setup_tooltips_event(tooltips) {{
            for (let k = 0; k < tooltips.tooltips.length; k++) {{
                $(tooltips.tooltips[k].selector).tooltip({{
                    template: `<div class="tooltip" role="tooltip">
                        <div class="tooltip-arrow"></div>
                        <div class="tooltip-inner"></div>
                    </div>`,
                    title: tooltips.tooltips[k].content,
                    html: true,
                    placement: "right",
                    fallbackPlacement: "flip",
                    animation: false,
                    trigger: "hover focus",
                    viewport: {{
                        selector: 'body',
                    }}
                }});
            }}
        }}
        let json_input = {json_input}

        let has_loaded = new Array(json_input.length);
        for (let i = 0; i < json_input.length; i++) {{
            let chart_config = json_input[i];
            chart_config.chart.callback.onTreeLoaded = function () {{}};
            let tree = new Treant(chart_config);
            if (i == 0) {{
                setup_tooltips_event(chart_config);
            }}
            $('#spectab' + i).on('shown.bs.tab', function (e) {{
                if (!has_loaded[i]) {{
                    tree.tree.reload();
                    setup_tooltips_event(chart_config);
                }}
                has_loaded[i] = true
            }});
            has_loaded[0] = true
        }}</script></body></html>"""
        return html_string

    @staticmethod
    def export_html(html: str, file_name: str = "tree.html") -> None:
        """Creates a html file in current directory"""
        text_file = open(file_name, "w", encoding="UTF8")
        text_file.write(html)
        text_file.close()

    def show(self) -> None:
        """Displays the forest in the web browser"""
        html_string = self.to_html()
        viewer = HTMLViewer()
        viewer.open_html(html_string)


class HTMLViewer:
    """A class for opening html text in browser."""

    _THREAD_WAIT_TIME: ClassVar[float] = 4  # seconds

    @staticmethod
    def _remove_file_thread(fname: str) -> None:
        time.sleep(HTMLViewer._THREAD_WAIT_TIME)
        if os.path.exists(fname):
            os.remove(fname)

    @staticmethod
    def _remove_file(fname: str) -> None:
        threading.Thread(target=HTMLViewer._remove_file_thread, args=(fname,)).start()
        logger.info("specification html file removed")

    @staticmethod
    def open_html(html: str) -> None:
        """Open and render html string in browser."""
        with tempfile.NamedTemporaryFile(
            "r+", suffix=".html", delete=False, encoding="UTF8"
        ) as html_file:
            html_file.write(html)
            webbrowser.open_new_tab(f"file://{html_file.name}")
            logger.info("Opening specification in browser")
            HTMLViewer._remove_file(html_file.name)

    @staticmethod
    def open_svg(svg: str) -> None:
        """Open and render svg image string in browser."""
        HTMLViewer.open_html(f"<html><body>{svg}</body></html>")
