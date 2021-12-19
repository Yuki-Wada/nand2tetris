from typing import List
import re
from Tokenizer import Tokenizer
from Parser import Parser
from XMLWriter import XMLWriter


class JackAnalyzer:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.parser = Parser(
            'compiler_config.json',
        )

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

    def tokenize(self, input_path: str):
        content = ''
        with open(input_path, 'r') as f:
            for line in f.readlines():
                line = self.cleanse_line(line)
                if line:
                    content += line + ' '

        content = self.remove_comment(content)
        tokens = self.tokenizer.tokenize(content)

        return tokens

    def parse(self, tokens: List[str]):
        return self.parser.parse(tokens, 'class')


def diff(input_path: str, output_path: str):
    print(input_path, output_path)
    with open(input_path, 'r') as f, open(output_path, 'r') as g:
        input_lines = f.readlines()
        output_lines = g.readlines()

    for i, (input_line, output_line) in \
            enumerate(zip(input_lines, output_lines)):
        if input_line == output_line:
            continue
        print(i + 1)
        print(input_line, output_line)


def compile(input_path: str, output_path: str, rightxml_path: str):
    jack_analyzer = JackAnalyzer()
    tokens = jack_analyzer.tokenize(input_path)
    token_tree = jack_analyzer.parse(tokens)

    xml_writer = XMLWriter()
    xml_writer.write_xml(token_tree, output_path)

    diff(rightxml_path, output_path)


def get_output_path(input_path: str):
    output_path = '.'.join(input_path.split('.')[:-1]) + 'Output.xml'
    return output_path


def get_rightxml_path(input_path: str):
    output_path = '.'.join(input_path.split('.')[:-1]) + '.xml'
    return output_path


def run():
    input_paths = [
        'ArrayTest/Test.jack',
        'ArrayTest/Main.jack',
        'ExpressionLessSquare/Main.jack',
        'ExpressionLessSquare/Square.jack',
        'ExpressionLessSquare/SquareGame.jack',
        'Square/Main.jack',
        'Square/Square.jack',
        'Square/SquareGame.jack',
    ]

    for input_path in input_paths:
        output_path = get_output_path(input_path)
        rightxml_path = get_rightxml_path(input_path)
        compile(input_path, output_path, rightxml_path)


if __name__ == '__main__':
    run()
