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
from typing import TYPE_CHECKING, ClassVar, Dict, List, TypedDict

from .combinatorial_class import CombinatorialClass
from .strategies import EquivalencePathRule, Rule, VerificationRule

if TYPE_CHECKING:
    from .specification import CombinatorialSpecification

TreantNode = TypedDict(
    "TreantNode", {"innerHTML": str, "collapsable": bool, "children": list}
)


class SpecificationDrawer:
    """
    A specification drawer is for visualizing CombinatorialSpecification by making
    HTML file that contains an interactive tree using the Treant javascript library

    https://fperucic.github.io/treant-js/
    Treant library converts a json of TreantNodes to HTML code
    """

    def __init__(self, spec: "CombinatorialSpecification"):
        self.spec = spec
        self.tooltips: List[Dict[str, str]] = []
        self._rules_dict_copy = copy(spec.rules_dict)
        self._current_node_id = 0
        self.tree_dict = self._to_tree_dict(spec.root)

    @property
    def rules_dict(self):
        """Original rules_dict from CombinatorialSpecification."""
        return self.spec.rules_dict

    def _get_new_node_id(self) -> int:
        self._current_node_id += 1
        return self._current_node_id

    def _to_tree_dict(self, comb_class: CombinatorialClass) -> TreantNode:
        """
        Create the subtree rooted in comb_class
        """
        try:
            # checks if the rule has come before
            rule = self._rules_dict_copy.pop(comb_class)
        except KeyError:
            # recursion
            return self._handle_recursion(comb_class)
        if isinstance(rule, EquivalencePathRule):
            child = rule.children[0]
            try:
                rule = self._rules_dict_copy.pop(child)
            except KeyError:
                # rule has recurred before
                return self._handle_recursion(rule.comb_class)
            comb_classes = [comb_class, rule.comb_class]
        else:
            comb_classes = [comb_class]
        treant_node = self._create_standard_node(comb_classes)
        self._create_standard_tooltip(comb_classes, self._current_node_id)

        children = [self._to_tree_dict(child) for child in rule.children]

        # If a node has children we create a delimiter node between them
        # in order to seperate tooltip describing the steps taking in the tree

        if children and isinstance(rule, Rule):
            delimiter_node = self._create_delimiter_node(rule, children)
            self._create_delimiter_tooltip(rule, self._current_node_id)
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

    def _create_standard_node(
        self, comb_classes: List[CombinatorialClass]
    ) -> TreantNode:
        """
        Takes in a list of comb_classes and merges them into a single node.
        Returns a standard treant node.
        """
        new_id = self._get_new_node_id()
        node_html = self.comb_classes_to_html_node(comb_classes)
        treant_node = TreantNode(
            innerHTML=f'<div id="node{new_id}" data-toggle="tooltip">{node_html}</div>',
            collapsable=False,
            children=[],
        )
        return treant_node

    def _create_delimiter_node(
        self, rule: Rule, children: List[TreantNode]
    ) -> TreantNode:
        """
        Returns delimiter node that describes
        the steps taken between the rule and their children
        """
        new_id = self._get_new_node_id()
        symbol = rule.strategy.get_op_symbol()
        delimiter_html = f'<div class="and-gate" id={new_id}>{symbol}</div>'
        delimiter_node = TreantNode(
            innerHTML=f"""<div id="node{new_id}"
                data-toggle="tooltip">{delimiter_html}</div>""",
            collapsable=True,
            children=children,
        )
        return delimiter_node

    def comb_classes_to_html_node(self, comb_classes: List[CombinatorialClass]) -> str:
        """
        Returns a representation of comb classes as a single html node string
        """
        if not comb_classes:
            raise RuntimeError("comb_classes is empty")
        html = ""
        style = ""
        # Check if comb_class has html representation function
        try:
            nodes = [comb_class.to_html_representation() for comb_class in comb_classes]
            style = "border-style:none"
        except NotImplementedError:
            nodes = [
                str(comb_class).replace("\n", "<br>") for comb_class in comb_classes
            ]

        if len(nodes) == 1:
            html += nodes[0]
        elif len(nodes) > 1:
            # eqv_rule
            for i, node_string in enumerate(nodes):
                if i == len(nodes) - 1:  # remove margin on last node
                    html += f"""<div class=eqv-node-content
                        style="margin-right:0;{style}">{node_string}</div>"""
                else:
                    html += f"""<div class=eqv-node-content style="{style}">
                        {node_string}</div>"""
        else:
            raise ValueError("comb_classes does not contain any string ....")

        # add labels above the node
        labels = [str(self.spec.get_label(comb_class)) for comb_class in comb_classes]
        labels_string = ", ".join(labels)
        labels_html = f"<div class=label>{labels_string}</div>"
        return f"{labels_html}<div class=node-content>{html}</div>"

    def _handle_recursion(self, comb_class: CombinatorialClass) -> TreantNode:
        """Returns standard tooltip and a TreantNode without any children"""
        assert comb_class in self.rules_dict
        # creates node without children
        treant_node = self._create_standard_node([comb_class])
        self._create_standard_tooltip([comb_class], self._current_node_id)
        return treant_node

    def to_treant_json(self) -> str:
        """
        Returns a json with a treant configuration with tooltips
        """
        return json.dumps(
            [
                {
                    "chart": {
                        "container": "#combo-tree0",
                        "connectors": {"type": "bCurve", "style": {}},
                        "nodeAlign": "BOTTOM",
                        "levelSeparation": 35,
                        "siblingSeparation": 30,
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
    def to_html_string(treant_json: str) -> str:
        """
        Returns a html string that contains the whole tree
        """
        html_head = """
        <!DOCTYPE html><html><head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>ComboPal</title>
        <link rel="stylesheet"
            href="https://combopal.ru.is/static/css/bootstrap.min.css">
        <link rel="stylesheet" href="https://combopal.ru.is/static/css/Treant.css">
        <link rel="stylesheet" href="https://combopal.ru.is/static/css/combopal.css">
        <style>
            .node-content{
                text-align: left;
                border: 1px solid;
                padding: 28px;
                font-family: Consolas, monaco, monospace;
                font-size: 14px; font-style: normal;
                line-height: normal;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .eqv-node-content{
                margin-right: 16px;
                max-width: 400px;
                border: 1px solid;
                padding: 16px;
            }
            .tooltip{
                opacity: 0.97 !important;
            }
            .tooltip-inner{
                font-family: Consolas, monaco, monospace;
                font-size: 14px;
                font-style: normal;
                line-height: normal;
                max-width: none !important;
            }
            .tiling{
                border: 1px solid;
                width: 22px;
                height: 22px;
                text-align: center;
            }
            .label{
                border: 1px solid;
                border-bottom-style: none;
            }
            pre{
                font-family: Consolas, monaco, monospace;
                font-size: 14px; font-style: normal;
                line-height: normal;
            }
            @media print {
                body {-webkit-print-color-adjust: exact;}
            }
        </style>
        <script
        src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js">
        </script>
        <script src="https://combopal.ru.is/static/js/bootstrap.bundle.min.js"></script>
        <script src="https://combopal.ru.is/static/js/Treant.js"></script>
        <script src="https://combopal.ru.is/static/js/raphael.js"></script>
        </head>
        """
        html_body_before_json = """
        <div id="combotabcontent0" class="tab-pane container active">
            <div id="combo-tree0" class="Treant Treant-loaded" style="width: 1080px;">
        </div></div>
        <script>
            function fix_tree_size(tree_css) {
            let tree_css_svg = tree_css + '> svg';
            var tree_actual_width = $(tree_css_svg).width();
            var pixels = tree_actual_width + "px";
            $(tree_css).css("width", pixels);
        }

        function setup_tooltips_event(tooltips) {
            for (let k = 0; k < tooltips.tooltips.length; k++) {
                $(tooltips.tooltips[k].selector).tooltip({
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
                    viewport: {
                        selector: 'body',
                    }
                });
            }
        }
        """
        html_body_after_json = """
            for (let i = 0; i < json_input.length; i++) {
                let chart_config = json_input[i];
                chart_config.chart.callback.onTreeLoaded = function () {
                    fix_tree_size(chart_config.chart.container);
                };
                let tree = new Treant(chart_config);
                if (i == 0) {
                    setup_tooltips_event(chart_config);
                }
                $('#combotab' + i).on('shown.bs.tab', function (e) {
                    tree.tree.reload();
                    setup_tooltips_event(chart_config);
                });
            }</script></body></html>"""
        html_string = html_head + html_body_before_json
        html_string += "\n let json_input =" + treant_json
        html_string += html_body_after_json
        return html_string

    @staticmethod
    def export_html(html: str, file_name: str = "tree") -> None:
        """
        Creates a html file in current directory
        """
        file_name += ".html"
        text_file = open(file_name, "w")
        text_file.write(html)
        text_file.close()

    def show(self):
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
            "r+", suffix=".html", delete=False
        ) as html_file:
            html_file.write(html)
            webbrowser.open_new_tab(f"file://{html_file.name}")
            HTMLViewer._remove_file(html_file.name)

    @staticmethod
    def open_svg(svg: str) -> None:
        """Open and render svg image string in browser."""
        HTMLViewer.open_html(f"<html><body>{svg}</body></html>")
