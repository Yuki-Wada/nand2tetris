import re


class SymbolTable:
    def __init__(self):
        self.symbol2address = {
            'SP': 0,
            'LCL': 1,
            'ARG': 2,
            'THIS': 3,
            'THAT': 4,
            'SCREEN': 16384,
            'KBD': 23576,
        }
        for i in range(16):
            self.symbol2address[f'R{i}'] = i
        self.current_var_address = 16

    def register_label(self, label_name, address):
        self.symbol2address[label_name] = address

    def register_var(self, var_name):
        if var_name not in self.symbol2address:
            self.symbol2address[var_name] = self.current_var_address
            self.current_var_address += 1

    def get_address(self, symbol_name):
        return self.symbol2address[symbol_name]


class OrderEncoder:
    def __init__(self):
        self.symbol_table = SymbolTable()

    def register_label(self, label, address):
        self.symbol_table.register_label(label, address)

    def register_var(self, var):
        self.symbol_table.register_var(var)

    def encode_comp(self, token):
        token2code = {
            '0': '0101010',
            '1': '0111111',
            '-1': '0111010',
            'D': '0001100',
            'A': '0110000',
            '!D': '0001101',
            '!A': '0110001',
            '-D': '0001111',
            '-A': '0110011',
            'D+1': '0011111',
            'A+1': '0110111',
            'D-1': '0001110',
            'A-1': '0110010',
            'D+A': '0000010',
            'D-A': '0010011',
            'A-D': '0000111',
            'D&A': '0000000',
            'D|A': '0010101',

            'M': '1110000',
            '!M': '1110001',
            '-M': '1110011',
            'M+1': '1110111',
            'M-1': '1110010',
            'D+M': '1000010',
            'D-M': '1010011',
            'M-D': '1000111',
            'D&M': '1000000',
            'D|M': '1010101',
        }

        return int(token2code[token], 2)

    def encode_dest(self, token):
        token2code = {
            '': 0,
            'M': 1,
            'D': 2,
            'MD': 3,
            'A': 4,
            'AM': 5,
            'AD': 6,
            'AMD': 7,
        }
        return token2code[token]

    def encode_jump(self, token):
        token2code = {
            '': 0,
            'JGT': 1,
            'JEQ': 2,
            'JGE': 3,
            'JLT': 4,
            'JNE': 5,
            'JLE': 6,
            'JMP': 7,
        }
        return token2code[token]

    def encode_a_order(self, value):
        address = value
        if isinstance(value, str):
            address = self.symbol_table.get_address(value)

        return f'0{address:015b}'

    def encode_c_order(self, dest, comp, jump):
        comp_bits = self.encode_comp(comp)
        dest_bits = self.encode_dest(dest)
        jump_bits = self.encode_jump(jump)

        return f'111{comp_bits:07b}{dest_bits:03b}{jump_bits:03b}'

    def encode(self, parsed):
        code = ''
        if parsed[0] == 'A':
            code = self.encode_a_order(parsed[1])
        elif parsed[0] == 'C':
            code = self.encode_c_order(
                parsed[1], parsed[2], parsed[3])

        return code


class HackAssembler:
    def __init__(self):
        self.order_encoder = OrderEncoder()
        self.parsed_asms = []

    def cleanse_line(self, line):
        match = re.search(r'//', line)
        if match is not None:
            line = line[:match.start()]
        line, _ = re.subn(r'\s', '', line)

        return line

    def parse_a_order(self, line):
        value = line[1:]
        if value.isdecimal():
            value = int(value)

        return ['A', value]

    def parse_c_order(self, line):
        elems = line.split(';')
        if len(elems) == 2:
            dest_comp, jump = elems
        else:
            dest_comp = elems[0]
            jump = ''

        elems = dest_comp.split('=')
        if len(elems) == 2:
            dest, comp = elems
        else:
            dest = ''
            comp = elems[0]

        return ['C', dest, comp, jump]

    def parse(self, line):
        line = self.cleanse_line(line)

        parsed = []
        if line.startswith('@'):
            parsed = self.parse_a_order(line)
        elif line:
            match = re.match(r'\((?P<label>.+)\)', line)
            if match is not None:
                label = match.group('label')
                self.order_encoder.register_label(
                    label, len(self.parsed_asms),
                )
            else:
                parsed = self.parse_c_order(line)

        if parsed:
            self.parsed_asms.append(parsed)

        return parsed

    def analyze_symbol(self):
        for parsed in self.parsed_asms:
            if parsed[0] == 'A' and isinstance(parsed[1], str):
                self.order_encoder.register_var(parsed[1])

    def encode(self):
        codes = []
        for parsed in self.parsed_asms:
            if not parsed:
                continue

            code = self.order_encoder.encode(parsed)
            if code:
                codes.append(code)

        return codes


def asm2bin(input_path, output_path):
    hack_assembler = HackAssembler()

    with open(input_path, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            hack_assembler.parse(line)

    hack_assembler.analyze_symbol()
    codes = hack_assembler.encode()
    with open(output_path, 'w') as f:
        for code in codes:
            f.write(code)
            f.write('\n')


def get_output_path(input_path):
    output_path = '.'.join(input_path.split('.')[:-1]) + '.hack'
    return output_path


def run():
    input_paths = [
        '06/add/Add.asm',
        '06/max/MaxL.asm',
        '06/max/Max.asm',
        '06/rect/RectL.asm',
        '06/rect/Rect.asm',
        '06/pong/PongL.asm',
        '06/pong/Pong.asm',
    ]
    for input_path in input_paths:
        output_path = get_output_path(input_path)
        asm2bin(input_path, output_path)


if __name__ == '__main__':
    run()
