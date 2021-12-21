import os
from typing import List
import re
from Tokenizer import Tokenizer
from Parser import Parser
from Converter import Converter
from XMLWriter import XMLWriter


class JackAnalyzer:
    def __init__(self):
        self.tokenizer = Tokenizer()

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


def write_vms(vms, output_path):
    with open(output_path, 'w') as f:
        for vm in vms:
            if isinstance(vm, list):
                vm = ' '.join([str(elem) for elem in vm])
            f.write(vm + '\n')


def diff(input_path: str, output_path: str):
    print(input_path, output_path)
    with open(input_path, 'r') as f, open(output_path, 'r') as g:
        input_lines = f.readlines()
        output_lines = g.readlines()

    inputlabel2outputlabel = {}
    for i, (input_line, output_line) in \
            enumerate(zip(input_lines, output_lines)):
        if input_line == output_line:
            continue

        input_commands = input_line.split()
        output_commands = output_line.split()
        if input_commands[0] in ['label', 'goto', 'if-goto'] and \
                input_commands[0] == output_commands[0] and \
                len(input_commands) == len(output_commands):
            if input_commands[1] not in inputlabel2outputlabel:
                inputlabel2outputlabel[input_commands[1]] = output_commands[1]
                continue
            if inputlabel2outputlabel[input_commands[1]] == output_commands[1]:
                continue

        print(i + 1)
        print(input_line, output_line)


def compile(
    input_path: str,
    xml_output_path: str,
    vm_output_path: str,
    vm_right_path: str,
):
    jack_analyzer = JackAnalyzer()
    tokens = jack_analyzer.tokenize(input_path)

    parser = Parser('compiler_config.json')
    token_tree = parser.parse(tokens)

    xml_writer = XMLWriter()
    xml_writer.write_xml(token_tree, xml_output_path)

    converter = Converter()
    vms = converter.convert(token_tree)
    write_vms(vms, vm_output_path)
    diff(vm_output_path, vm_right_path)


def get_xml_output_path(input_path: str):
    output_dir_path = os.path.join(
        os.path.dirname(input_path), 'Output',
    )
    os.makedirs(output_dir_path, exist_ok=True)
    input_file_name = os.path.basename(input_path)

    output_path = os.path.join(
        output_dir_path,
        '.'.join(input_file_name.split('.')[:-1]) + '.xml',
    )
    return output_path


def get_vm_output_path(input_path: str):
    output_dir_path = os.path.join(
        os.path.dirname(input_path), 'Output',
    )
    os.makedirs(output_dir_path, exist_ok=True)
    input_file_name = os.path.basename(input_path)

    output_path = os.path.join(
        output_dir_path,
        '.'.join(input_file_name.split('.')[:-1]) + '.vm',
    )
    return output_path


def get_vm_right_path(input_path: str):
    output_dir_path = os.path.dirname(input_path)
    input_file_name = os.path.basename(input_path)

    output_path = os.path.join(
        output_dir_path,
        '.'.join(input_file_name.split('.')[:-1]) + '.vm',
    )
    return output_path


def run():
    input_paths = [
        'Seven/Main.jack',
        'ConvertToBin/Main.jack',
        'Square/Main.jack',
        'Square/Square.jack',
        'Square/SquareGame.jack',
        'Average/Main.jack',
        'Pong/Main.jack',
        'Pong/Ball.jack',
        'Pong/Bat.jack',
        'Pong/PongGame.jack',
        'ComplexArrays/Main.jack',
    ]

    for input_path in input_paths:
        xml_output_path = get_xml_output_path(input_path)
        vm_output_path = get_vm_output_path(input_path)
        vm_right_path = get_vm_right_path(input_path)
        compile(input_path, xml_output_path, vm_output_path, vm_right_path)


if __name__ == '__main__':
    run()
