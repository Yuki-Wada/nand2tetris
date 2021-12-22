import re
from Tokenizer import Tokenizer
from Parser import Parser
from XMLWriter import XMLWriter


def get_output_path(input_path: str):
    output_path = '.'.join(input_path.split('.')[:-1]) + 'Output.xml'
    return output_path


def get_rightxml_path(input_path: str):
    output_path = '.'.join(input_path.split('.')[:-1]) + '.xml'
    return output_path


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
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize_file(input_path)

    parser = Parser('compiler_config.json')
    token_tree = parser.parse(tokens)
    xml_writer = XMLWriter()
    xml_writer.write_xml(token_tree, output_path)

    diff(rightxml_path, output_path)


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
