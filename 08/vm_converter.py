import os
import random
import string
import re


class LabelTag:
    def __init__(self, label_type):
        #         self.label_type = 'define', 'static' or 'temp'
        self.label_type = label_type


class LabelManager:
    def __init__(self):
        self.used_labels = set()

    def get_label(self):
        while True:
            label = ''.join([
                random.choice(string.ascii_letters + string.digits) for i in range(16)
            ])
            if label not in self.used_labels:
                self.used_labels.add(label)
                return label

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


class VMEncoder:
    def __init__(self, input_path):
        self.file_name = '.'.join(os.path.basename(input_path).split('.')[:-1])

        self.unary_arithmetic_command_set = set(['neg', 'not'])
        self.binary_arithmetic_command_set = set([
            'add', 'sub', 'eq', 'gt', 'lt', 'and', 'or',
        ])
        self.memory_access_command_set = set(['push', 'pop'])
        self.program_flow_command_set = set(['label', 'goto', 'if-goto'])
        self.subroutine_command_set = set(['function', 'call', 'return'])

        self.label_manager = LabelManager()

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
            label_dest, label_branch = self.label_manager.get_labels()

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

    def encode_static_memory_access_command(self, command, index):
        asms = []

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

    def encode_memory_access_command(self, commands):
        command, segment, index = commands

        if segment == 'static':
            return self.encode_static_memory_access_command(
                command, index,
            )

        asms = []
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

    def encode_program_flow_command(self, commands):
        command, label = commands

        asms = []
        if command == 'label':
            asms.append(f'({label})')
        elif command == 'goto':
            asms.append(f'@{label}')
            asms.append(f'0;JMP')
        elif command == 'if-goto':
            asms.append(f'@0')
            asms.append(f'M=M-1')
            asms.append(f'A=M')
            asms.append(f'D=M')
            asms.append(f'@{label}')
            asms.append(f'D;JNE')
        else:
            raise ValueError('Not implemented')

        return asms

    def encode_subroutine_command(self, commands):
        command = commands[0]

        asms = []
        if command == 'call':
            _, function_name, argc = commands
            argc = int(argc)

            label = self.label_manager.get_label()

            asms.append(f'@{label}')
            asms.append(f'D=A')

            asms.append(f'@0')
            asms.append(f'A=M')
            asms.append(f'M=D')
            asms.append(f'@0')
            asms.append(f'M=M+1')

            for i in range(4):
                asms.append(f'@{i+1}')
                asms.append(f'D=M')

                asms.append(f'@0')
                asms.append(f'A=M')
                asms.append(f'M=D')
                asms.append(f'@0')
                asms.append(f'M=M+1')

            asms.append(f'@0')
            asms.append(f'D=M')
            asms.append(f'@1')
            asms.append(f'M=D')
            asms.append(f'@{argc + 5}')
            asms.append(f'D=D-A')
            asms.append(f'@2')
            asms.append(f'M=D')

            asms.append(f'@{function_name}')
            asms.append(f'0;JMP')

            asms.append(f'({label})')

        elif command == 'function':
            _, function_name, argc = commands
            argc = int(argc)

            asms.append(f'({function_name})')

            for _ in range(argc):
                asms.append(f'@0')
                asms.append(f'D=A')

                asms.append(f'@0')
                asms.append(f'A=M')
                asms.append(f'M=D')
                asms.append(f'@0')
                asms.append(f'M=M+1')

        elif command == 'return':
            asms.append(f'@1')
            asms.append(f'D=M')
            asms.append(f'@0')
            asms.append(f'A=M')
            asms.append(f'M=D')

            asms.append(f'@0')
            asms.append(f'A=M')
            asms.append(f'D=M')
            asms.append(f'@5')
            asms.append(f'A=D-A')
            asms.append(f'D=M')
            asms.append(f'@0')
            asms.append(f'A=M+1')
            asms.append(f'M=D')

            asms.append(f'@0')
            asms.append(f'A=M-1')
            asms.append(f'D=M')
            asms.append(f'@2')
            asms.append(f'A=M')
            asms.append(f'M=D')

            asms.append(f'@2')
            asms.append(f'D=M+1')
            asms.append(f'@0')
            asms.append(f'A=M+1')
            asms.append(f'A=A+1')
            asms.append(f'M=D')

            for i in range(4):
                asms.append(f'@0')
                asms.append(f'A=M')
                asms.append(f'D=M')
                asms.append(f'@{i+1}')
                asms.append(f'A=D-A')
                asms.append(f'D=M')
                asms.append(f'@{4-i}')
                asms.append(f'M=D')

            asms.append(f'@0')
            asms.append(f'A=M+1')
            asms.append(f'D=M')
            asms.append(f'@0')
            asms.append(f'A=M+1')
            asms.append(f'A=A+1')
            asms.append(f'A=M')
            asms.append(f'M=D')

            asms.append(f'@0')
            asms.append(f'A=M+1')
            asms.append(f'A=A+1')
            asms.append(f'D=M')
            asms.append(f'@0')
            asms.append(f'M=D')

            asms.append(f'A=D')
            asms.append(f'A=M')
            asms.append(f'0;JMP')

        else:
            raise ValueError('Not implemented')

        return asms

    def encode(self, commands):
        command = commands[0]
        if command in self.memory_access_command_set:
            return self.encode_memory_access_command(commands)
        if command in self.unary_arithmetic_command_set:
            return self.encode_unary_arithmetic_command(commands)
        if command in self.binary_arithmetic_command_set:
            return self.encode_binary_arithmetic_command(commands)
        if command in self.program_flow_command_set:
            return self.encode_program_flow_command(commands)
        if command in self.subroutine_command_set:
            return self.encode_subroutine_command(commands)


class VMParser:
    def __init__(self, input_path):
        self.input_path = input_path
        self.commands = []
        with open(self.input_path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                command = self.parse(line)
                if command:
                    self.commands.append(command)

    def cleanse_line(self, line):
        match = re.search(r'//', line)
        if match is not None:
            line = line[:match.start()]
        line = line.strip()

        return line

    def parse(self, line):
        line = self.cleanse_line(line)
        command = line.split()

        return command


class VMConverter:
    def __init__(self):
        self.vm_parsers = []

    def parse_file(self, input_path):
        input_paths = []
        if os.path.isdir(input_path):
            for file_name in os.listdir(input_path):
                if file_name.endswith('.vm'):
                    file_path = os.path.join(input_path, file_name)
                    input_paths.append(file_path)
        else:
            input_paths.append(input_path)

        for input_path in input_paths:
            vm_parser = VMParser(input_path)
            self.vm_parsers.append(vm_parser)

    def analysis(self):
        pass

    def convert(self):
        asms = []

        for vm_parser in self.vm_parsers:
            vm_encoder = VMEncoder(vm_parser.input_path)
            for command in vm_parser.commands:
                asms += vm_encoder.encode(command)

        for asm in asms:
            if asm == '(Sys.init)':
                vm_encoder = VMEncoder('')
                init_asms = []
                init_asms.append('@256')
                init_asms.append('D=A')
                init_asms.append('@0')
                init_asms.append('M=D')
                init_asms += vm_encoder.encode(['call', 'Sys.init', '0'])
                asms = init_asms + asms
                break

        return asms


def vm2asm(input_path, output_path):
    vm_converter = VMConverter(input_path)

    vm_converter.parse_file(input_path)
    vm_converter.analysis()
    asms = vm_converter.convert()

    with open(output_path, 'w') as f:
        for asm in asms:
            f.write(asm)
            f.write('\n')


def get_output_path(input_path):
    if os.path.isdir(input_path):
        file_name = os.path.basename(input_path) + '.asm'
        output_path = os.path.join(input_path, file_name)
    else:
        output_path = '.'.join(input_path.split('.')[:-1]) + '.asm'
    return output_path


def run():
    input_paths = [
        '07/StackArithmetic/SimpleAdd/SimpleAdd.vm',
        '07/StackArithmetic/StackTest/StackTest.vm',
        '07/MemoryAccess/BasicTest/BasicTest.vm',
        '07/MemoryAccess/PointerTest/PointerTest.vm',
        '07/MemoryAccess/StaticTest/StaticTest.vm',
        '08/ProgramFlow/BasicLoop/BasicLoop.vm',
        '08/ProgramFlow/FibonacciSeries/FibonacciSeries.vm',
        '08/FunctionCalls/SimpleFunction/SimpleFunction.vm',
        '08/FunctionCalls/FibonacciElement',
        '08/FunctionCalls/NestedCall',
        '08/FunctionCalls/StaticsTest',
    ]

    for input_path in input_paths:
        output_path = get_output_path(input_path)
        vm2asm(input_path, output_path)


if __name__ == '__main__':
    run()
