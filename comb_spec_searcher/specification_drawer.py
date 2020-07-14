"""
A specification drawer is for visualizing combinatorial specification object
"""
import json
from copy import copy
from typing import Any, Dict, List

from .combinatorial_class import CombinatorialClassType
from .specification import CombinatorialSpecification
from .strategies import EquivalencePathRule, Rule, VerificationRule


class SpecificationDrawer:
    """
    A specification drawer is for visualizing CombinatorialSpecification
    by creating interactive tree using javascript library
    """

    def __init__(self, spec: CombinatorialSpecification):
        self.spec = spec
        self.tooltips: List[dict] = []
        self._rules_dict_copy = copy(spec.rules_dict)

    def rules_to_html_representation(
        self, comb_classes: List[CombinatorialClassType]
    ) -> str:
        """
        Returns a single node containing the rules as html string
        """
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
        if len(nodes) > 1:
            # eqv_rule
            for i, node_string in enumerate(nodes):
                if i == len(nodes) - 1:  # remove margin on last node
                    html += """<div class=eqv-node-content
                        style="margin-right:0;{}">{}</div>""".format(
                        style, node_string
                    )
                else:
                    html += """<div class=eqv-node-content style="{}">
                    {}</div>""".format(
                        style, node_string
                    )
        elif len(nodes) == 1:
            html = nodes[0]
        return "<div class=node-content>{}</div>".format(html)

    def _create_delimiter_tooltip(self, rule: Rule, node_identifier: int) -> None:
        """
        Creates hover over tooltip for delimiter node
        """
        tooltip = {
            "content": """
                <p>Formal step:<br/>{}</p>
            """.format(
                rule.formal_step
            )
        }
        tooltip["selector"] = "#node{}".format(node_identifier)
        self.tooltips.append(tooltip)

    def _create_standard_tooltip(
        self, comb_classes: List[CombinatorialClassType], node_identifier: int
    ) -> None:
        """
        Creates hover over tooltip for standard node
        """
        rule = self.spec.get_rule(comb_classes[0])
        if isinstance(rule, EquivalencePathRule):
            # need to use the rule to be able to see the whole eqv path
            rule_string = str(rule).replace("\n", "<br>")
        else:
            rule_string = str(comb_classes[0]).replace("\n", "<br>")
        labels = [str(self.spec.get_label(comb_class)) for comb_class in comb_classes]
        labels_string = ", ".join(labels)
        tooltip = {
            "content": """
                <p>Labels: {}</p>
                <pre><br/>{}</pre>
            """.format(
                labels_string, rule_string,
            )
        }
        if isinstance(rule, VerificationRule):
            tooltip["content"] += "<p>Verified: {}</p>".format(rule.formal_step)
        tooltip["selector"] = "#node{}".format(node_identifier)
        self.tooltips.append(tooltip)

    def _create_standard_node(
        self, comb_classes: List[CombinatorialClassType]
    ) -> Dict[str, Any]:
        """
        Takes in a list of comb_classes and merges them into a single node.
        Returns a standard treant node.
        """
        node_identifier = len(self.tooltips)  # id for tooltips to recognize
        node_html = self.rules_to_html_representation(comb_classes)
        treant_node = {
            "innerHTML": """<div id="node{}" data-toggle="tooltip">
            {}</div>""".format(
                node_identifier, node_html
            ),
            "collapsable": False,
        }
        self._create_standard_tooltip(comb_classes, node_identifier)
        return treant_node

    def _create_delimiter_node(self, rule: Rule) -> Dict[str, Any]:
        """
        Takes in rule and its children as list of treant nodes.
        Returns a delimiter node.
        """
        node_identifier = len(self.tooltips)  # id for tooltips to recognize
        symbol = rule.constructor.get_op_symbol()
        delimiter_html = '<div class="and-gate" id={}>{}</div>'.format(
            node_identifier, symbol
        )
        delimiter_node = {
            "innerHTML": """<div id="node{}" data-toggle="tooltip">
                {}</div>""".format(
                node_identifier, delimiter_html
            ),
            "collapsable": True,
        }
        self._create_delimiter_tooltip(rule, node_identifier)
        return delimiter_node

    def _handle_eqv_path_rule(
        self, eqv_rule: EquivalencePathRule
    ) -> List[CombinatorialClassType]:
        """
        Process the EquivalencePathRule by getting each rule that is
        equivalent to that rule and returns their comb_classes
        """
        eqv_comb_classes = [eqv_rule.comb_class]
        try:
            child = self._rules_dict_copy.pop(eqv_rule.children[0])
            if isinstance(child, EquivalencePathRule):
                eqv_comb_classes += self._handle_eqv_path_rule(child)
            else:
                # eqv path ended
                eqv_comb_classes.append(child.comb_class)
        except KeyError:
            # rule has recurred before
            assert eqv_rule.children[0].comb_class in self.spec.rules_dict
            eqv_comb_classes.append(child.comb_class)
            # TODO make a node without children
        return eqv_comb_classes

    def _to_tree_dict_rec(self, comb_class: CombinatorialClassType) -> Dict[str, Any]:
        """
        Makes the tree recursively and returns a tree dict
        """
        try:
            # checks if the rule has come before
            rule = self._rules_dict_copy.pop(comb_class)
        except KeyError:
            # recursion
            assert comb_class in self.spec.rules_dict
            # creates node without children
            return self._create_standard_node([comb_class])

        if isinstance(rule, EquivalencePathRule):
            comb_classes: List[CombinatorialClassType]
            comb_classes = self._handle_eqv_path_rule(rule)
            treant_node = self._create_standard_node(comb_classes)
            # children of eqv are stored in the last index
            rule = self.spec.get_rule(comb_classes[-1])
        else:
            treant_node = self._create_standard_node([comb_class])

        children = [self._to_tree_dict_rec(child) for child in rule.children]

        # If a node has children we create a delimeter node between them
        # in order to seperate tooltip describing the steps taking in the tree

        if children and isinstance(rule, Rule):
            delimiter_node = self._create_delimiter_node(rule)
            delimiter_node["children"] = children
            children = [delimiter_node]

        treant_node["children"] = children
        return treant_node

    def to_tree_dict(self, comb_class: CombinatorialClassType) -> dict:
        """
        Returns a dictionary containing a tree structure
        for treant javascript library
        """
        self.tooltips = []
        self._rules_dict_copy = copy(self.spec.rules_dict)
        return self._to_tree_dict_rec(comb_class)

    def tree_to_treant_json(self, tree_dict: dict) -> str:
        """
        Returns a json with a treant configuration with tooltips
        """
        return json.dumps(
            [
                {
                    "chart": {
                        "container": "#combo-tree{}".format(0),
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
                    "nodeStructure": tree_dict,
                    "tooltips": self.tooltips,
                }
            ]
        )

    def to_html_string(self, treant_json: str) -> str:
        """
        Returns a html string that contains the whole tree
        """
        a = """
        <!DOCTYPE html><html><head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>ComboPal</title>
        <link rel="stylesheet"
            href="https://combopal.ru.is/static/css/bootstrap.min.css">
        <link rel="stylesheet"
            href="https://combopal.ru.is/static/css/Treant.css">
        <link rel="stylesheet"
            href="https://combopal.ru.is/static/css/combopal.css">
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
                float:left;
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
        <script
        src="https://combopal.ru.is/static/js/bootstrap.bundle.min.js">
        </script>
        <script src="https://combopal.ru.is/static/js/Treant.js"></script>
        <script src="https://combopal.ru.is/static/js/raphael.js"></script>
        </head>
        """
        b = """
        <div id="combotabcontent0" class="tab-pane container active">
        <div id="combo-tree0" class="Treant Treant-loaded"
        style="width: 1080px;"></div>
        </div>
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
        c = """
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
        html_string = a + b + "\n" + "let json_input =" + treant_json + c
        return html_string

    def export_html(self, html: str, file_name: str = "tree") -> None:
        """
        Creates a html file in current directory
        """
        file_name += ".html"
        text_file = open(file_name, "w")
        text_file.write(html)
        text_file.close()

    def draw_tree(self) -> str:
        """
        return a html file in a string format containing
        a tree structure of this specification
        """
        tree_dict = self.to_tree_dict(self.spec.root)
        treant_json = self.tree_to_treant_json(tree_dict)
        return self.to_html_string(treant_json)
