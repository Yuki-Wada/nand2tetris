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


def compile(input_path: str, xml_output_path: str, vm_output_path: str):
    jack_analyzer = JackAnalyzer()
    tokens = jack_analyzer.tokenize(input_path)

    parser = Parser('compiler_config.json')
    token_tree = parser.parse(tokens)

    xml_writer = XMLWriter()
    xml_writer.write_xml(token_tree, xml_output_path)

    converter = Converter()
    vms = converter.convert(token_tree)
    write_vms(vms, vm_output_path)


def get_xml_output_path(input_path: str):
    output_path = '.'.join(input_path.split('.')[:-1]) + '.xml'
    return output_path


def get_vm_output_path(input_path: str):
    output_path = '.'.join(input_path.split('.')[:-1]) + '_Output.vm'
    return output_path


def run():
    input_paths = [
        'Seven/Main.jack',
        # 'ConvertToBin/Main.jack',
        # 'Square/Main.jack',
        # 'Square/Square.jack',
        # 'Square/SquareGame.jack',
        # 'Average/Main.jack',
        # 'Pong/Main.jack',
        # 'Pong/Ball.jack',
        # 'Pong/Bat.jack',
        # 'Pong/PongGame.jack',
        # 'ComplexArrays/Main.jack',
    ]

    for input_path in input_paths:
        xml_output_path = get_xml_output_path(input_path)
        vm_output_path = get_vm_output_path(input_path)
        compile(input_path, xml_output_path, vm_output_path)


if __name__ == '__main__':
    run()
