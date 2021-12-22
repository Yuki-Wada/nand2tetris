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

    def cleanse_line(self, line: str):
        match = re.search(r'//', line)
        if match is not None:
            line = line[:match.start()]
        line = line.strip()

        return line

    def remove_comment(self, raw_content: str):
        content = ''
        i = 0
        in_comment = False
        while i < len(raw_content):
            if not in_comment and raw_content[i:i + 2] == '/*':
                in_comment = True
                i += 2
                continue
            elif in_comment and raw_content[i:i + 2] == '*/':
                in_comment = False
                i += 2
                continue

            if not in_comment:
                content += raw_content[i]

            i += 1

        return content

    def tokenize_file(self, input_path: str):
        content = ''
        with open(input_path, 'r') as f:
            for line in f.readlines():
                line = self.cleanse_line(line)
                if line:
                    content += line + ' '

        content = self.remove_comment(content)
        tokens = self.tokenize(content)

        return tokens
