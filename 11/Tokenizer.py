import re

keyword_set = set([
    'class', 'constructor', 'function', 'method', 'field',
    'static', 'var', 'int', 'char', 'boolean', 'void',
    'true', 'false', 'null', 'this', 'let', 'do',
    'if', 'else', 'while', 'return',
])
symbol_set = set('{}()[].,;+-*/&|<>=~?')


def get_token_type(token: str):
    if token in keyword_set:
        return 'keyword'
    if token in symbol_set:
        return 'symbol'
    if re.match(r'".*"', token):
        return 'stringConstant'
    if token.isnumeric():
        return 'integerConstant'
    if re.match(r'[a-zA-Z][a-zA-Z0-9]*', token):
        return 'identifier'

    raise ValueError('Wrong token type')


def is_token_type(token: str, token_type: str):
    if token_type == 'keywordConstant':
        return token in keyword_set
    if token_type == 'integerConstant':
        return token.isnumeric()
    if token_type == 'stringConstant':
        return token.startswith('"')
    if token_type == 'identifier':
        return re.match(r'[a-zA-Z][a-zA-Z0-9]*', token) is not None

    return False


def is_symbol(chars):
    return chars in symbol_set


class Tokenizer:
    def __init__(self):
        self.keyword_set = set([
            'class', 'constructor', 'function', 'method', 'field',
            'static', 'var', 'int', 'char', 'boolean', 'void',
            'true', 'false', 'null', 'this', 'let', 'do',
            'if', 'else', 'while', 'return',
        ])
        self.symbols = '{}()[].,;+-*/&|<>=~?'
        self.alphabet_pattern = re.compile(r'[a-zA-Z0-9_]')

    def tokenize(self, line):
        tokens = []

        token = ''
        in_quote = False
        for c in line:
            if in_quote:
                token += c
                if c == '"':
                    tokens.append(token)
                    token = ''
                    in_quote = False
            else:
                if c in self.symbols:
                    if token:
                        tokens.append(token)
                        token = ''
                    tokens.append(c)
                elif c == ' ':
                    if token:
                        tokens.append(token)
                        token = ''
                elif c == '"':
                    if token:
                        tokens.append(token)
                    token = c
                    in_quote = True
                else:
                    if self.alphabet_pattern.match(c):
                        token += c
                    else:
                        raise ValueError()

        if token:
            tokens.append(token)

        return tokens
