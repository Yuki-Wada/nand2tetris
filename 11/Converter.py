from __future__ import annotations
from typing import Optional
from TokenTree import TokenTree
from SymbolTable import SymbolTable


class Converter:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_class_name: Optional[str] = None
        self.current_subroutine_name: Optional[str] = None

    def convert_class(self, tree: TokenTree):
        # "class": "'class' className '{' classVarDec* subroutineDec* '}'",
        nodes = tree.nodes
        class_name = nodes[1].single_token

        self.current_class_name = class_name

        vms = []
        for node in nodes:
            if node.label != 'subroutineDec':
                continue
            vms += self.convert_subroutine_dec(node)

        return vms

    def convert_class_var_dec(self, tree: TokenTree):
        # "classVarDec": "('static' | 'field') type varName (',' varName)* ';'",
        raise NotImplementedError('You should not Call This Function')

    def convert_type(self, tree: TokenTree):
        # "type": "'int' | 'char' | 'boolean' | className",
        raise NotImplementedError('You should not Call This Function')

    def convert_subroutine_dec(self, tree: TokenTree):
        # "subroutineDec": "('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody",
        nodes = tree.nodes
        subroutine_name = nodes[2].single_token
        subroutine_body_node = nodes[6]

        self.current_subroutine_name = subroutine_name

        class_name = self.current_class_name
        argument_count = self.symbol_table.get_subroutine_local_variable_count(
            self.current_class_name, subroutine_name,
        )
        return_type, subroutine_attr = self.symbol_table.get_subroutine_info(
            self.current_class_name, subroutine_name,
        )

        vms = []
        vms.append([
            'function',
            f'{class_name}.{subroutine_name}',
            argument_count,
        ])

        if subroutine_attr == 'method':
            vms.append(['push', 'argument', 0])
            vms.append(['pop', 'pointer', 0])
        elif subroutine_attr == 'constructor':
            class_memory_size = self.symbol_table.get_class_field_count(
                self.current_class_name
            )
            vms.append(['push', 'constant', class_memory_size])
            vms.append(['call', 'Memory.alloc', 1])
            vms.append(['pop', 'pointer', '0'])
        elif subroutine_attr == 'function':
            pass
        else:
            raise NotImplementedError('Unexpected Subroutine Attribute')

        vms += self.convert_subroutine_body(subroutine_body_node, return_type)

        return vms

    def convert_parameter_list(self, tree: TokenTree):
        # "parameterList": "((type varName) (',' type varName)*)?",
        raise NotImplementedError('You should not Call This Function')

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
        raise NotImplementedError('You should not Call This Function')

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
        raise NotImplementedError('Unexpected Statement Label')

    def convert_let_statement(self, tree: TokenTree):
        # "letStatement": "'let' varName ('[' expression ']' )? '=' expression ';'",
        nodes = tree.nodes
        var_name = nodes[1].single_token
        is_array = len(nodes) == 8

        variable_info = self.symbol_table.get_variable_info(
            self.current_class_name, self.current_subroutine_name, var_name,
        )
        if variable_info is None:
            raise ValueError('Undefined Variable')
        _, var_type, var_order = variable_info

        vms = []
        if is_array:
            vms += self.convert_expression(nodes[3])
            vms.append(['push', var_type, var_order])
            vms.append('add')

            vms += self.convert_expression(nodes[-2])
            vms.append(['pop', 'temp', 0])

            vms.append(['pop', 'pointer', 1])
            vms.append(['push', 'temp', 0])
            vms.append(['pop', 'that', 0])
        else:
            vms += self.convert_expression(nodes[-2])
            vms.append(['pop', var_type, var_order])

        return vms

    def convert_if_statement(self, tree: TokenTree):
        # "ifStatement": "'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?",
        nodes = tree.nodes
        expression_node = nodes[2]
        if_statements_node = nodes[5]
        exists_else_statement = len(nodes) == 11

        label1 = self.symbol_table.generate_label()
        label2 = self.symbol_table.generate_label()
        label3 = self.symbol_table.generate_label()

        vms = []
        vms += self.convert_expression(expression_node)
        vms.append(['if-goto', label1])

        if exists_else_statement:
            label3 = self.symbol_table.generate_label()

            vms.append(['goto', label2])
            vms.append(['label', label1])
            vms += self.convert_statements(if_statements_node)
            vms.append(['goto', label3])

            vms.append(['label', label2])
            else_statements_node = nodes[9]
            vms += self.convert_statements(else_statements_node)
            vms.append(['label', label3])
        else:
            vms.append(['goto', label2])
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

        vms = []
        vms.append(['label', label1])
        vms += self.convert_expression(expression_node)
        vms.append(['not'])
        vms.append(['if-goto', label2])
        vms += self.convert_statements(statements_node)
        vms.append(['goto', label1])
        vms.append(['label', label2])

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

        # if nodes[0].label == 'varName':
        #     variable_info = self.symbol_table.get_variable_info(
        #         self.current_class_name, self.current_subroutine_name, nodes[0].single_token)
        #     if variable_info is None:
        #         raise ValueError('Undefined Variable')
        #     _, var_type, var_order = variable_info
        #     vms = [['push', var_type, var_order]]
        #     return vms

        if nodes[0].label == 'identifier':
            is_array = len(nodes) == 4

            variable_info = self.symbol_table.get_variable_info(
                self.current_class_name, self.current_subroutine_name, nodes[0].single_token)
            if variable_info is None:
                raise ValueError('Undefined Variable')
            _, var_type, var_order = variable_info

            vms = []
            if is_array:
                vms += self.convert_expression(nodes[2])
                vms.append(['push', var_type, var_order])
                vms.append('add')
                vms.append(['pop', 'pointer', 1])
                vms.append(['push', 'that', 0])
            else:
                vms = [['push', var_type, var_order]]

            return vms

        if nodes[0].single_token == '(':
            return self.convert_expression(nodes[1])

        if nodes[0].label == 'unaryOp':
            vms = self.convert_term(nodes[1])
            vms += self.convert_unary_op(nodes[0])
            return vms

        if nodes[0].label == 'integerConstant':
            vms = [['push', 'constant', nodes[0].single_token]]
            return vms

        if nodes[0].label == 'stringConstant':
            vms = self.convert_string_constant(nodes[0])
            return vms

        if nodes[0].label == 'keyword':
            vms = self.convert_keyword_constant(nodes[0])
            return vms

        raise NotImplementedError('Unexpected Term')

    def convert_subroutine_call(self, tree: TokenTree):
        # "subroutineCall": "subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'",
        nodes = tree.nodes

        expression_list_node = nodes[-2]

        vms = []

        argument_count = (len(expression_list_node.nodes) + 1) // 2
        if len(nodes) == 4:
            class_name = self.current_class_name
            subroutine_name = nodes[0].single_token

            _, subroutine_attr = self.symbol_table.get_subroutine_info(
                self.current_class_name, subroutine_name)
            if subroutine_attr in ['function', 'constructor']:
                pass
            elif subroutine_attr == 'method':
                argument_count += 1
                vms.append(['push', 'pointer', 0])
            else:
                raise NotImplementedError('Unexpected Subroutine Attribute')

        elif len(nodes) == 6:
            variable_info = self.symbol_table.get_variable_info(
                self.current_class_name,
                self.current_subroutine_name,
                nodes[0].single_token,
            )
            if variable_info is None:
                class_name = nodes[0].single_token
            else:
                class_name, var_type, var_order = variable_info
                vms.append(['push', var_type, var_order])
                argument_count += 1
            subroutine_name = nodes[2].single_token
        else:
            raise NotImplementedError('Wrong Subroutine Call Format')

        vms += self.convert_expression_list(expression_list_node)
        vms.append(
            ['call', f'{class_name}.{subroutine_name}', argument_count])

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
            raise NotImplementedError('Unexpected Binary Operation')

        return vms

    def convert_unary_op(self, tree: TokenTree):
        # "unaryOp": "'-' | '~'",
        vms = []

        op = tree.nodes[0].single_token
        if op == '-':
            vms.append('neg')
        elif op == '~':
            vms.append('not')
        else:
            raise NotImplementedError('Unexpected Unary Operation')

        return vms

    def convert_string_constant(self, tree: TokenTree):
        string_constant = tree.single_token

        vms = []
        vms.append(['push', 'constant', len(string_constant)])
        vms.append(['call', 'String.new', 1])
        for ch in string_constant:
            vms.append(['push', 'constant', ord(ch)])
            vms.append(['call', 'String.appendChar', 2])

        return vms

    def convert_keyword_constant(self, tree: TokenTree):
        keyword = tree.single_token

        vms = []
        if keyword == 'true':
            vms.append(['push', 'constant', 0])
            vms.append('not')
        elif keyword == 'false':
            vms.append(['push', 'constant', 0])
        elif keyword == 'null':
            vms.append(['push', 'constant', 0])
        elif keyword == 'this':
            vms.append(['push', 'pointer', 0])
        else:
            raise NotImplementedError('Unexpected Unary Operation')
        return vms

    def convert(self, token_tree: TokenTree):
        self.symbol_table.analyze(token_tree)
        vms = self.convert_class(token_tree)

        return vms
