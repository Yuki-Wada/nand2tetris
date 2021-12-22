import os
import sys

sys.path.append('../11')

try:
    from Converter import Converter
    from Parser import Parser
    from Tokenizer import Tokenizer
except BaseException:
    pass


def get_paths(title: str):
    output_dir_path = f'{title}Test'

    return [
        [
            f'{title}.jack',
            os.path.join(output_dir_path, f'{title}.vm'),
        ],
        [
            os.path.join(output_dir_path, 'Main.jack'),
            os.path.join(output_dir_path, 'Main.vm'),
        ],
    ]


def write_vms(vms, output_path):
    with open(output_path, 'w') as f:
        for vm in vms:
            if isinstance(vm, list):
                vm = ' '.join([str(elem) for elem in vm])
            f.write(vm + '\n')


def compile(
    input_path: str,
    vm_output_path: str,


):
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize_file(input_path)

    parser = Parser('../11/compiler_config.json')
    token_tree = parser.parse(tokens)

    converter = Converter()
    vms = converter.convert(token_tree)
    write_vms(vms, vm_output_path)


def run():
    titles = [
        'Math',
        # 'String',
        # 'Array',
        # 'Output',
        # 'Screen',
        # 'Keyboard',
        # 'Memory',
        # 'Sys',
    ]

    for title in titles:
        for input_path, vm_output_path in get_paths(title):
            compile(input_path, vm_output_path)


if __name__ == '__main__':
    run()
