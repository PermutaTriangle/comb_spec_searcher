"""
A specification drawer is for visualizing combinatorial specification object
"""
import json
import os
import tempfile
import threading
import time
import webbrowser
from copy import copy
from typing import TYPE_CHECKING, ClassVar, Dict, List, Tuple

from typing_extensions import TypedDict

from .combinatorial_class import CombinatorialClass
from .strategies import EquivalencePathRule, Rule, VerificationRule

if TYPE_CHECKING:
    from .specification import CombinatorialSpecification


class TreantNode(TypedDict):
    innerHTML: str
    collapsable: bool
    collapsed: bool
    children: list


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
        self._current_node_id = 0
        self.levels_shown = levels_shown
        self.levels_expand = levels_expand
        self.tree_dict = self._to_tree_dict(spec.root)

    def _get_new_node_id(self) -> int:
        self._current_node_id += 1
        return self._current_node_id

    def _to_tree_dict(
        self, comb_class: CombinatorialClass, rec_depth: int = 0
    ) -> TreantNode:
        """
        Create the subtree rooted in comb_class
        """
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
            children = [
                self._to_tree_dict(child, rec_depth + 1) for child in rule.children
            ]

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

    def _create_delimiter_tooltip(self, rule: Rule, node_identifier: int) -> None:
        """
        Creates hover over tooltip for delimiter node
        """
        tooltip = {
            "content": f"<p>Formal step:<br/>{rule.formal_step}</p>",
            "selector": f"#node{node_identifier}",
        }
        self.tooltips.append(tooltip)

    def _create_standard_tooltip(
        self, comb_classes: List[CombinatorialClass], node_identifier: int
    ) -> None:
        """
        Creates hover over tooltip for standard node
        """
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

    def _create_standard_node(self, html_node: str) -> Tuple[TreantNode, int]:
        """
        Returns a tuple containing a standard treant node and its id.
        """
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
    ) -> Tuple[TreantNode, int]:
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
        """
        Returns a representation of comb classes as a single html node string
        """
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
            inner_style += "border-style:none;"
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

    def to_treant_json(self) -> str:
        """
        Returns a json with a treant configuration with tooltips
        """
        return json.dumps(
            [
                {
                    "chart": {
                        "maxDepth": 10000,
                        "container": "#combo-tree0",
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
                    "nodeStructure": self.tree_dict,
                    "tooltips": self.tooltips,
                }
            ]
        )

    def to_html(self) -> str:
        """
        Return a html file in a string format containing
        a tree structure of this specification
        """
        treant_json = self.to_treant_json()
        return self.to_html_string(treant_json)

    @staticmethod
    def _read_file(filename):
        with open(filename, "r", encoding="UTF8") as f:
            return f.read()

    def to_html_string(self, treant_json: str) -> str:
        """
        Returns a html string that contains the whole tree
        """
        script_dir = os.path.dirname(__file__)
        # Path to static files
        psf = os.path.join(script_dir, "resources/static/")
        treant_stylesheet = self._read_file(os.path.join(psf, "css/treant.css"))
        combopal_stylesheet = self._read_file(os.path.join(psf, "css/combopal.css"))

        jquery_min_script = self._read_file(os.path.join(psf, "js/jquery.min.js"))
        bootstrap_min_script = self._read_file(
            os.path.join(psf, "js/bootstrap.bundle.min.js")
        )
        treant_script = self._read_file(os.path.join(psf, "js/Treant.js"))
        raphael_script = self._read_file(os.path.join(psf, "js/raphael.js"))

        html_string = f"""
        <!DOCTYPE html><html><head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>ComboPal</title>
        <style>
        {treant_stylesheet}
        {combopal_stylesheet}
        </style>
        <script>{jquery_min_script}</script>
        <script>{bootstrap_min_script}</script>
        <script>{treant_script}</script>
        <script>{raphael_script}</script>
        <div id="combo-tree0" class="Treant Treant-loaded"></div>
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
        let json_input = {treant_json}
            for (let i = 0; i < json_input.length; i++) {{
                let chart_config = json_input[i];
                chart_config.chart.callback.onTreeLoaded = function () {{

                }};
                let tree = new Treant(chart_config);
                if (i == 0) {{
                    setup_tooltips_event(chart_config);
                }}
                $('#combotab' + i).on('shown.bs.tab', function (e) {{
                    tree.tree.reload();
                    setup_tooltips_event(chart_config);
                }});
            }}</script></body></html>"""
        return html_string

    @staticmethod
    def export_html(html: str, file_name: str = "tree") -> None:
        """
        Creates a html file in current directory
        """
        file_name += ".html"
        text_file = open(file_name, "w", encoding="UTF8")
        text_file.write(html)
        text_file.close()

    def show(self):
        """
        Displays CombinatorialSpecification tree in the web browser
        """
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

    @staticmethod
    def open_html(html: str) -> None:
        """Open and render html string in browser."""
        with tempfile.NamedTemporaryFile(
            "r+", suffix=".html", delete=False, encoding="UTF8"
        ) as html_file:
            html_file.write(html)
            webbrowser.open_new_tab(f"file://{html_file.name}")
            HTMLViewer._remove_file(html_file.name)

    @staticmethod
    def open_svg(svg: str) -> None:
        """Open and render svg image string in browser."""
        HTMLViewer.open_html(f"<html><body>{svg}</body></html>")
