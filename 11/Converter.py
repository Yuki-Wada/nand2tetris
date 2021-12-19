from __future__ import annotations
from typing import List, Optional
from TokenTree import TokenTree
from SymbolTable import SymbolTable


class Converter:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_class_name: Optional[str] = None

    def convert_class(self, tree: TokenTree):
        # "class": "'class' className '{' classVarDec* subroutineDec* '}'",
        nodes = tree.nodes

        self.current_class_name = nodes[1].single_token

        vms = []
        for node in nodes:
            if node.label != 'subroutineDec':
                continue
            vms += self.convert_subroutine_dec(node)

        return vms

    def convert_class_var_dec(self, tree: TokenTree):
        # "classVarDec": "('static' | 'field') type varName (',' varName)* ';'",
        raise NotImplemented()

    def convert_type(self, tree: TokenTree):
        # "type": "'int' | 'char' | 'boolean' | className",
        raise NotImplemented()

    def convert_subroutine_dec(self, tree: TokenTree):
        # "subroutineDec": "('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody",
        nodes = tree.nodes
        subroutine_name = nodes[2].single_token
        subroutine_body_node = nodes[6]

        class_name = self.current_class_name
        argument_count = self.symbol_table.get_subroutine_argument_count(
            self.current_class_name, subroutine_name,
        )
        return_type, subroutine_attr = self.symbol_table.get_subroutine_info(
            self.current_class_name, subroutine_name,
        )

        vms = []
        vms.append([
            subroutine_attr,
            f'{class_name}.{subroutine_name}',
            argument_count,
        ])

        if subroutine_attr == 'method':
            vms.append(['push', 'argument', 0])
            vms.append(['pop', 'pointer', 0])

        vms += self.convert_subroutine_body(subroutine_body_node, return_type)

        return vms

    def convert_parameter_list(self, tree: TokenTree):
        # "parameterList": "((type varName) (',' type varName)*)?",
        raise NotImplemented()

    def convert_subroutine_body(
        self, tree: TokenTree, return_type: str,
    ):
        # "subroutineBody": "'{' varDec* statements '}'",
        nodes = tree.nodes

        vms = []
        vms += self.convert_statements(nodes[-2])

        return vms

    def convert_var_dec(self, tree: TokenTree):
        # "varDec": "'var' type varName (',' varName)* ';'",
        raise NotImplemented()

    def convert_statements(self, tree: TokenTree):
        # "statements": "statement*",
        nodes = tree.nodes
        lines = []
        for node in nodes:
            lines += self.convert_statement(node)
        return lines

    def convert_statement(self, tree: TokenTree):
        # "statement": "letStatement | ifStatement | whileStatement | doStatement | returnStatement",
        node = tree.nodes[0]
        if node.label == 'letStatement':
            return self.convert_let_statement(node)
        if node.label == 'ifStatement':
            return self.convert_if_statement(node)
        if node.label == 'whileStatement':
            return self.convert_while_statement(node)
        if node.label == 'doStatement':
            return self.convert_do_statement(node)
        if node.label == 'returnStatement':
            return self.convert_return_statement(node)
        raise NotImplemented()

    def convert_let_statement(self, tree: TokenTree):
        # "letStatement": "'let' varName ('[' expression ']' )? '=' expression ';'",
        nodes = tree.nodes
        var_name = nodes[1].label
        var_type, var_order = self.symbol_table.get_variable_info(
            self.current_class_name, var_name,
        )

        vms = []
        if len(nodes) == 8:
            vms += self.convert_expression(nodes[3])
        else:
            vms += self.convert_expression(nodes[6])
        vms.append(['pop', var_type, var_order])

        return vms

    def convert_if_statement(self, tree: TokenTree):
        # "ifStatement": "'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?",
        nodes = tree.nodes
        expression_node = nodes[2]
        if_statements_node = nodes[5]

        label1 = self.symbol_table.generate_label()
        label2 = self.symbol_table.generate_label()

        vms = []
        vms += self.convert_expression(expression_node)
        vms.append(['if-goto', label1])

        if len(nodes) == 11:
            else_statements_node = nodes[9]
            vms += self.convert_statements(else_statements_node)

        vms.append(['if-goto', label2])
        vms.append(['label', label1])
        vms += self.convert_statements(if_statements_node)
        vms.append(['label', label2])

        return vms

    def convert_while_statement(self, tree: TokenTree):
        # "whileStatement": "'while' '(' expression ')' '{' statements '}'",
        expression_node = tree.nodes[2]
        statements_node = tree.nodes[5]

        label1 = self.symbol_table.generate_label()
        label2 = self.symbol_table.generate_label()
        label3 = self.symbol_table.generate_label()

        vms = []
        vms.append(['label', label1])
        vms += self.convert_expression(expression_node)
        vms.append(['if-goto', label2])
        vms.append(['goto', label3])
        vms.append(['label', label2])
        vms += self.convert_statements(statements_node)
        vms.append(['goto', label1])
        vms.append(['label', label3])

        return vms

    def convert_do_statement(self, tree: TokenTree):
        # "doStatement": "'do' subroutineCall ';'",
        node = tree.nodes[1]

        vms = []
        vms += self.convert_subroutine_call(node)
        vms.append(['pop', 'temp', 0])

        return vms

    def convert_return_statement(self, tree: TokenTree):
        # "returnStatement": "'return' expression? ';'",
        nodes = tree.nodes

        vms = []
        if len(nodes) == 3:
            vms += self.convert_expression(nodes[1])
        else:
            vms.append(['push', 'constant', 0])
        vms.append(['return'])

        return vms

    def convert_expression(self, tree: TokenTree):
        # "expression": "term (op term)*",
        nodes = tree.nodes
        vms = []

        i = 0
        while i < len(nodes):
            vms += self.convert_term(nodes[i])
            if i > 0:
                vms += self.convert_op(nodes[i - 1])
            i += 2

        return vms

    def convert_term(self, tree: TokenTree):
        # "term": "subroutineCall | varName '[' expression ']' | '(' expression ')' | unaryOp term | integerConstant | stringConstant | keywordConstant | varName",
        nodes = tree.nodes

        if nodes[0].label == 'subroutineCall':
            return self.convert_subroutine_call(nodes[0])
        if nodes[0].label == 'varName':
            var_type, var_order = self.symbol_table.get_variable_info(
                nodes[0].single_token)
            vms = [['push', var_type, var_order]]
            return vms
        if nodes[0].single_token == '(':
            return self.convert_expression(nodes[1])
        if nodes[0].label == 'subroutine':
            vms = self.convert_expression(nodes[1])
            vms += self.convert_unary_op(nodes[0])
            return vms
        if nodes[0].label == 'integerConstant':
            vms = [['push', 'constant', nodes[0].single_token]]
            return vms
        if nodes[0].label == 'stringConstant':
            vms = [['push', 'constant', nodes[0].single_token]]
            return vms
        if nodes[0].label == 'keywordConstant':
            vms = [['push', 'constant', nodes[0].single_token]]
            return vms

        raise NotImplemented()

    def convert_subroutine_call(self, tree: TokenTree):
        # "subroutineCall": "subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'",
        nodes = tree.nodes

        expression_list_node = nodes[-2]

        vms = []
        if len(nodes) == 4:
            class_name = self.current_class_name
            subroutine_name = nodes[0].single_token
        elif len(nodes) == 6:
            class_name = nodes[0].single_token
            subroutine_name = nodes[2].single_token
        else:
            raise NotImplemented()

        argument_count = (len(expression_list_node.nodes) + 1) // 2
        vms += self.convert_expression_list(expression_list_node)
        vms.append(['call', f'{class_name}.{subroutine_name}', argument_count])

        return vms

    def convert_expression_list(self, tree: TokenTree):
        # "expressionList": "(expression (',' expression)* )?",
        nodes = tree.nodes
        vms = []

        i = 0
        while i < len(nodes):
            vms += self.convert_expression(nodes[i])
            i += 2

        return vms

    def convert_op(self, tree: TokenTree):
        # "op": "'+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='",
        vms = []

        op = tree.nodes[0].single_token
        if op == '+':
            vms.append('add')
        elif op == '-':
            vms.append('sub')
        elif op == '*':
            vms.append('call Math.multiply 2')
        elif op == '/':
            vms.append('call Math.divide 2')
        elif op == '&':
            vms.append('and')
        elif op == '|':
            vms.append('or')
        elif op == '<':
            vms.append('lt')
        elif op == '>':
            vms.append('gt')
        elif op == '=':
            vms.append('eq')
        else:
            raise NotImplemented()

        return vms

    def convert_unary_op(self, tree: TokenTree):
        # "unaryOp": "'-' | '~'",
        vms = []

        op = tree.nodes[0]
        if op == '-':
            vms.append('neg')
        if op == '~':
            vms.append('not')

        return vms

    def convert_keyword_constant(self, tree: TokenTree):
        raise NotImplemented()

    def convert(self, token_tree: TokenTree):
        self.symbol_table.analyze(token_tree)
        vms = self.convert_class(token_tree)

        return vms
