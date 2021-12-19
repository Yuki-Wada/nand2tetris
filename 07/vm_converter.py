import os
import random
import string
import re


class VMConverter:
    def __init__(self, input_path):
        self.file_name = '.'.join(os.path.basename(input_path).split('.')[:-1])

        self.asms = []

        self.unary_arithmetic_command_set = set(['neg', 'not'])
        self.binary_arithmetic_command_set = set([
            'add', 'sub', 'eq', 'gt', 'lt', 'and', 'or',
        ])
        self.memory_access_command_set = set(['push', 'pop'])

        self.used_labels = set()

    def get_labels(self):
        while True:
            label_org = ''.join([
                random.choice(string.ascii_letters + string.digits) for i in range(16)
            ])
            label_dest = f'{label_org}_dest'
            label_branch = f'{label_org}_branch'
            if label_dest not in self.used_labels and label_branch not in self.used_labels:
                self.used_labels.add(label_dest)
                self.used_labels.add(label_branch)
                return label_dest, label_branch

    def encode_unary_arithmetic_command(self, commands):
        asms = []

        asms.append(f'@0')
        asms.append(f'M=M-1')
        asms.append(f'A=M')
        asms.append(f'D=M')

        command, = commands
        if command == 'neg':
            asms.append(f'D=-D')
        elif command == 'not':
            asms.append(f'D=!D')
        else:
            raise ValueError('Not implemented')

        asms.append(f'@0')
        asms.append(f'A=M')
        asms.append(f'M=D')
        asms.append(f'@0')
        asms.append(f'M=M+1')

        return asms

    def encode_binary_arithmetic_command(self, commands):
        asms = []

        asms.append(f'@0')
        asms.append(f'M=M-1')
        asms.append(f'A=M')
        asms.append(f'D=M')

        asms.append(f'@0')
        asms.append(f'M=M-1')
        asms.append(f'A=M')

        command, = commands
        if command == 'add':
            asms.append(f'D=M+D')
        elif command == 'sub':
            asms.append(f'D=M-D')
        elif command == 'and':
            asms.append(f'D=M&D')
        elif command == 'or':
            asms.append(f'D=M|D')
        elif command in ['eq', 'gt', 'lt']:
            label_dest, label_branch = self.get_labels()

            asms.append('D=M-D')
            asms.append(f'@{label_branch}')

            if command in 'eq':
                asms.append('D;JEQ')
            elif command == 'gt':
                asms.append('D;JGT')
            elif command == 'lt':
                asms.append('D;JLT')
            else:
                raise ValueError('Not implemented')

            asms.append(f'D=0')
            asms.append(f'@{label_dest}')
            asms.append(f'0;JMP')
            asms.append(f'({label_branch})')
            asms.append(f'D=-1')
            asms.append(f'({label_dest})')

        else:
            raise ValueError('Not implemented')

        asms.append(f'@0')
        asms.append(f'A=M')
        asms.append(f'M=D')
        asms.append(f'@0')
        asms.append(f'M=M+1')

        return asms

    def encode_memory_access_command(self, commands):
        asms = []
        command, segment, index = commands

        if segment == 'static':
            label = f'{self.file_name}.{index}'
            if command == 'push':
                asms.append(f'@{label}')
                asms.append(f'D=M')

                asms.append(f'@0')
                asms.append(f'A=M')
                asms.append(f'M=D')
                asms.append(f'@0')
                asms.append(f'M=M+1')

            if command == 'pop':
                asms.append(f'@0')
                asms.append(f'A=M-1')
                asms.append(f'D=M')
                asms.append(f'@{label}')
                asms.append(f'M=D')

                asms.append(f'@0')
                asms.append(f'M=M-1')

            return asms

        asms.append(f'@{index}')
        asms.append(f'D=A')
        if segment == 'local':
            asms.append(f'@1')
            asms.append(f'D=D+M')
        elif segment == 'argument':
            asms.append(f'@2')
            asms.append(f'D=D+M')
        elif segment == 'this':
            asms.append(f'@3')
            asms.append(f'D=D+M')
        elif segment == 'that':
            asms.append(f'@4')
            asms.append(f'D=D+M')
        elif segment == 'pointer':
            asms.append(f'@3')
            asms.append(f'D=D+A')
        elif segment == 'temp':
            asms.append(f'@5')
            asms.append(f'D=D+A')
        elif segment == 'constant':
            pass
        elif segment == 'static':
            pass
        else:
            raise ValueError('Not implemented')

        if command == 'push':
            if segment != 'constant':
                asms.append(f'A=D')
                asms.append(f'D=M')

            asms.append(f'@0')
            asms.append(f'A=M')
            asms.append(f'M=D')
            asms.append(f'@0')
            asms.append(f'M=M+1')

        elif command == 'pop':
            asms.append(f'@0')
            asms.append(f'A=M')
            asms.append(f'M=D')

            asms.append(f'@0')
            asms.append(f'A=M-1')
            asms.append(f'D=M')
            asms.append(f'@0')
            asms.append(f'A=M')
            asms.append(f'A=M')
            asms.append(f'M=D')

            asms.append(f'@0')
            asms.append(f'M=M-1')

        return asms

    def encode(self, commands):
        command = commands[0]
        if command in self.memory_access_command_set:
            return self.encode_memory_access_command(commands)
        if command in self.unary_arithmetic_command_set:
            return self.encode_unary_arithmetic_command(commands)
        if command in self.binary_arithmetic_command_set:
            return self.encode_binary_arithmetic_command(commands)

    def cleanse_line(self, line):
        match = re.search(r'//', line)
        if match is not None:
            line = line[:match.start()]
        line = line.strip()

        return line

    def parse(self, line):
        line = self.cleanse_line(line)
        parsed = line.split()

        if parsed:
            line_asms = self.encode(parsed)
            self.asms += line_asms
            return line_asms

        return []

    def get_asms(self):
        return self.asms


def vm2asm(input_path, output_path):
    vm_converter = VMConverter(input_path)

    with open(input_path, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            vm_converter.parse(line)

    asms = vm_converter.get_asms()
    with open(output_path, 'w') as f:
        for asm in asms:
            f.write(asm)
            f.write('\n')


def get_output_path(input_path):
    output_path = '.'.join(input_path.split('.')[:-1]) + '.asm'
    return output_path


def run():
    input_paths = [
        '07/StackArithmetic/SimpleAdd/SimpleAdd.vm',
        '07/StackArithmetic/StackTest/StackTest.vm',
        '07/MemoryAccess/BasicTest/BasicTest.vm',
        '07/MemoryAccess/PointerTest/PointerTest.vm',
        '07/MemoryAccess/StaticTest/StaticTest.vm',
    ]
    for input_path in input_paths:
        output_path = get_output_path(input_path)
        vm2asm(input_path, output_path)


if __name__ == '__main__':
    run()
