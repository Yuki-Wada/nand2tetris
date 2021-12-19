from __future__ import annotations
from typing import List
from ConfigExecuter import ConfigExecuter, \
    ConfigElementExecuter, \
    ConfigSequentialExecuter, \
    ConfigChoiceExecuter


class ExecuterFactory:
    @staticmethod
    def generate_from_config_tokens(
        config_tokens: List[str],
        label: str = '',
    ) -> ConfigExecuter:
        choice_executers: List[ConfigExecuter] = []
        sequential_executers: List[ConfigExecuter] = []

        parenthesis_count = 0
        tokens = []
        for token in config_tokens:
            if parenthesis_count > 0:
                if token == '(':
                    parenthesis_count += 1
                elif token == ')':
                    parenthesis_count -= 1
                tokens.append(token)
                if parenthesis_count == 0:
                    sequential_executers.append(
                        ExecuterFactory.generate_from_config_tokens(
                            tokens[:-1]
                        ))
                    tokens = []
            else:
                if token == '(':
                    parenthesis_count += 1
                elif token == ')':
                    raise ValueError()
                elif token in ['*', '?']:
                    sequential_executers.append(token)
                elif token == '|':
                    if len(sequential_executers) >= 2:
                        executer = ConfigSequentialExecuter(
                            'sequential', sequential_executers)
                        choice_executers.append(executer)
                    else:
                        executer = sequential_executers[0]
                        choice_executers.append(executer)
                    sequential_executers = []
                else:
                    sequential_executers.append(
                        ConfigElementExecuter('single', token)
                    )

        if sequential_executers:
            if len(sequential_executers) >= 2:
                executer = ConfigSequentialExecuter(
                    'sequential', sequential_executers)
                choice_executers.append(executer)
            else:
                executer = sequential_executers[0]
                choice_executers.append(executer)

        if len(choice_executers) == 1:
            executer = choice_executers[0]
            executer.label = label
            return executer

        return ConfigChoiceExecuter('choice', choice_executers, label)
