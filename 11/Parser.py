from __future__ import annotations
from typing import Dict
import re
import json
from Tokenizer import Tokenizer
from ConfigExecuter import ConfigExecuter
from ExecuterFactory import ExecuterFactory


class Parser:
    def __init__(self, config_path: str):
        self.label2executer: Dict[str, ConfigExecuter] = {}
        with open(config_path, 'r') as f:
            config_dict = json.load(f)

        tokenizer = Tokenizer()
        for label in config_dict:
            tokens = tokenizer.tokenize(re.sub("'", '"', config_dict[label]))
            self.label2executer[label] = ExecuterFactory.generate_from_config_tokens(
                tokens, label,
            )

    def parse(self, tokens, init_label='class'):
        return self.label2executer[init_label].execute(
            tokens, self.label2executer,
        )


if __name__ == '__main__':
    Parser('compiler_config.json')
