from __future__ import annotations
from typing import List
from TokenTree import TokenTree
from SymbolTable import SymbolTable
from TokenTree import TokenTree


class Converter:
    def __init__(self):
        pass

    def create_symbol_table(self, token_tree: TokenTree) -> SymbolTable:
        symbol_table = SymbolTable()

        def read(tree: TokenTree):
            for node in tree.nodes:
                if node.label == 'identifier':
                    symbol_table.register(node.single_token)
                else:
                    read(node)
        read(token_tree)

    def convert_class(self, tree):
        # "class": "'class' className '{' classVarDec* subroutineDec* '}'",
        pass

    def convert_statements(self, tree):
        # "statements": "statement*",
        nodes = tree.nodes
        lines = []
        for node in nodes:
            lines += self.convert_statement(node)
        return lines

    def convert_statement(self, tree):
        # "statement": "letStatement | ifStatement | whileStatement | doStatement | returnStatement",
        node = tree.nodes[0]
        if node.label == 'letStatement':
            return self.convert_let_statement(node)
        if node.label == 'ifStatement':
            return self.convert_let_statement(node)
        if node.label == 'whileStatement':
            return self.convert_let_statement(node)
        if node.label == 'doStatement':
            return self.convert_let_statement(node)
        if node.label == 'returnStatement':
            return self.convert_let_statement(node)

    def convert_let_statement(self, tree):
        # "letStatement": "'let' varName ('[' expression ']' )? '=' expression ';'",
        nodes = tree.nodes
        if nodes[2] == '[':
            pass
        else:
            i = 1

    def convert_if_statement(self, tree):
        # "ifStatement": "'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?",
        nodes = tree.nodes
        expression_node = nodes[2]
        if_statements_node = nodes[5]

        vms = []
        vms += self.convert_expression(expression_node)
        vms += self.convert_statements(if_statements_node)

        if len(nodes) == 11:
            else_statements_node = nodes[9]
            vms += self.convert_statements(else_statements_node)

        return vms

    def convert_while_statement(self, tree):
        # "whileStatement": "'while' '(' expression ')' '{' statements '}'",
        expression_node = tree.nodes[2]
        statements_node = tree.nodes[5]

        vms = []
        vms += self.convert_expression(expression_node)
        vms += self.convert_statements(statements_node)

        return vms

    def convert_do_statement(self, tree):
        # "doStatement": "'do' subroutineCall ';'",
        node = tree.nodes[1]

        vms = []
        vms += self.convert_subroutine_call(node)

        return vms

    def convert_return_statement(self, tree):
        # "returnStatement": "'return' expression? ';'",
        nodes = tree.nodes

        vms = []
        if len(nodes) == 2:
            vms += self.convert_expression(nodes[1])

        return vms

    def convert_expression(self, tree):
        # "expression": "term (op term)*",
        nodes = tree.nodes
        vms = []

        i = 0
        while i < len(nodes):
            vms += self.convert_term(nodes[i])
            if i > 0:
                self.convert_op(nodes[i - 1])
            i += 2

        return vms

    def convert_term(self, tree):
        # "term": "subroutineCall | varName '[' expression ']' | '(' expression ')' | unaryOp term | integerConstant | stringConstant | keywordConstant | varName",
        nodes = tree.nodes
        print(111)
        pass

    def convert_subroutine_call(self, tree):
        # "subroutineCall": "subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'",
        nodes = tree.nodes[0]

        vms = []
        if len(nodes) == 4:
            pass
        elif len(nodes) == 6:
            pass
        else:
            raise NotImplemented()

        return vms

    def convert_expression_list(self, tree):
        # "expressionList": "(expression (',' expression)* )?",
        nodes = tree.nodes
        vms = []

        i = 0
        while i < len(nodes):
            vms += self.convert_term(nodes[i])
            if i > 0:
                self.convert_op(nodes[i - 1])
            i += 2

        return vms

    def convert_op(self, tree):
        # "op": "'+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='",
        op = tree.nodes[0]
        vms = []

        raise NotImplemented()

        return vms

    def convert_unary_op(self, tree):
        # "unaryOp": "'-' | '~'",
        op = tree.nodes[0]
        vms = []

        raise NotImplemented()

    def convert_keyword_constant(self, tree):
        # "keywordConstant": "'true' | 'false' | 'null' | 'this'"
        op = tree.nodes[0]
        vms = []

        raise NotImplemented()

    def convert(
        self,
        token_tree: TokenTree,
        symbol_table: SymbolTable,
    ) -> List[str]:
        def read(tree: TokenTree):
            for node in tree.nodes:
                if node.label == 'expression':
                    self.convert_expression(node)
                else:
                    read(node)
        read(token_tree)

    def analyze(self, token_tree: TokenTree):
        symbol_table = self.create_symbol_table(token_tree)
        self.convert(token_tree, symbol_table)
