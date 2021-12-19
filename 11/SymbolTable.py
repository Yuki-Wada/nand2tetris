from typing import DefaultDict, List, Dict, Tuple, Set
from collections import defaultdict
import random
import string
from TokenTree import TokenTree


class SymbolTable:
    def __init__(self):
        self.var_count_dict: DefaultDict[Tuple[str, str], int] = \
            defaultdict(int)
        self.subroutine_count_dict: DefaultDict[Tuple[str, str, str], int] = \
            defaultdict(int)
        self.class_variable_table = []
        self.class_subroutine_table = []
        self.class_subroutine_variable_table = []
        self.used_labels: Set[str] = set()

    def analyze_class_var_dec(self, tree: TokenTree, class_name: str):
        # "classVarDec": "('static' | 'field') type varName (',' varName)* ';'",
        nodes = tree.nodes

        var_attr = nodes[0].single_token
        var_type = nodes[1].single_token

        i = 2
        while i < len(nodes):
            var_name = nodes[i].label
            if var_attr == 'static':
                count = self.var_count_dict[(class_name, var_attr)]
                self.count_dict[(class_name, var_attr)] += 1
            if var_attr == 'field':
                count = self.var_count_dict[(class_name, var_attr)]
                self.var_count_dict[(class_name, var_attr)] += 1
            self.class_variable_table.append([
                class_name, var_name, var_type, var_attr, count
            ])
            i += 2

    def analyze_parameter_list(
        self, tree: TokenTree, class_name: str, subroutine_name: str,
    ):
        # "parameterList": "((type varName) (',' type varName)*)?",
        nodes = tree.nodes
        var_attr = 'argument'

        i = 0
        while i < len(nodes):
            var_type = nodes[i].single_token
            var_name = nodes[i + 1].single_token

            argument_count = self.subroutine_count_dict[(
                class_name, subroutine_name, var_attr)]
            self.class_subroutine_variable_table.append([
                class_name, subroutine_name, var_name, var_type,
                var_attr, argument_count,
            ])
            self.subroutine_count_dict[(
                class_name, subroutine_name, var_attr)] += 1
            i += 3

    def analyze_var_dec(
        self, tree: TokenTree, class_name: str, subroutine_name: str,
    ):
        # "varDec": "'var' type varName (',' varName)* ';'",
        nodes = tree.nodes

        var_attr = 'var'
        var_type = nodes[1].single_token

        i = 2
        while i < len(nodes):
            var_name = nodes[i].single_token
            var_count = self.subroutine_count_dict[(
                class_name, subroutine_name, var_attr)]
            self.class_variable_table.append([
                class_name, subroutine_name, var_name, var_type,
                var_attr, var_count
            ])
            self.subroutine_count_dict[(
                class_name, subroutine_name, var_attr)] += 1
            i += 2

    def analyze_subroutine_body(
        self, tree: TokenTree, class_name: str, subroutine_name: str,
    ):
        # "subroutineBody": "'{' varDec* statements '}'",
        nodes = tree.nodes

        for node in nodes:
            if node.single_token == 'varDec':
                self.analyze_var_dec(node, class_name, subroutine_name)

    def analyze_subroutine_dec(self, tree: TokenTree, class_name: str):
        # "subroutineDec": "('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody",
        nodes = tree.nodes
        subroutine_name = nodes[2].single_token
        subroutine_attr = nodes[0].single_token
        return_type = nodes[1].single_token

        self.class_subroutine_table.append([
            class_name, subroutine_name, return_type, subroutine_attr,
        ])
        self.analyze_parameter_list(nodes[-3], class_name, subroutine_name)
        self.analyze_subroutine_body(nodes[-1], class_name, subroutine_name)

    def analyze_class(self, tree: TokenTree):
        # "class": "'class' className '{' classVarDec* subroutineDec* '}'",
        nodes = tree.nodes
        class_name = nodes[1].single_token

        for node in nodes:
            if node.label == 'classVarDec':
                self.analyze_class_var_dec(node, class_name)
            if node.label == 'subroutineDec':
                self.analyze_subroutine_dec(node, class_name)

    def get_subroutine_argument_count(
        self,
        target_class_name: str,
        target_subroutine_name: str,
    ):
        count = 0
        for info in self.class_subroutine_variable_table:
            class_name, subroutine_name, _, _, var_attr, _ = info
            if var_attr == 'argument' and target_class_name == class_name and \
                    target_subroutine_name == subroutine_name:
                count += 1
        return count

    def get_subroutine_local_variable_count(
        self,
        target_class_name: str,
        target_subroutine_name: str,
    ):
        count = 0
        for info in self.class_subroutine_variable_table:
            class_name, subroutine_name, _, _, var_attr, _ = info
            if var_attr == 'var' and target_class_name == class_name and \
                    target_subroutine_name == subroutine_name:
                count += 1
        return count

    def get_variable_info(
        self,
        target_class_name: str,
        target_var_name: str,
    ):
        for info in self.class_variable_table:
            class_name, var_name, _, var_attr, order = info
            if target_class_name == class_name and \
                    target_var_name == var_name:
                return [var_attr, order]

        raise ValueError('Undefined')

    def get_subroutine_info(
        self,
        target_class_name: str,
        target_subroutine_name: str,
    ):
        for info in self.class_subroutine_table:

            class_name, subroutine_name, return_type, subroutine_attr = info
            if target_class_name == class_name and \
                    target_subroutine_name == subroutine_name:
                return [return_type, subroutine_attr]

        raise ValueError('Undefined')

    def generate_label(self):
        while True:
            label = ''.join([
                random.choice(string.ascii_letters + string.digits) for i in range(16)
            ])
            if label not in self.used_labels:
                self.used_labels.add(label)
                return label

    def analyze(self, token_tree: TokenTree):
        def read(tree: TokenTree):
            if tree.label == 'class':
                self.analyze_class(tree)
            else:
                for node in tree.nodes:
                    read(node)
        read(token_tree)
