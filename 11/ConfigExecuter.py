from __future__ import annotations

import re
from typing import List, Dict, Tuple, Union, Optional
from TokenTree import TokenTree
from Tokenizer import get_token_type
from abc import ABCMeta, abstractmethod


class ConfigExecuter(metaclass=ABCMeta):
    @abstractmethod
    def analyze(
        self,
        tokens: List[str],
        label2executer: Dict[str, ConfigExecuter],
    ) -> Optional[Tuple[int, TokenTree]]:
        pass

    def execute(
        self,
        tokens: List[str],
        label2executer: Dict[str, ConfigExecuter],
    ) -> TokenTree:
        result = self.analyze(tokens, label2executer)
        if not result:
            raise ValueError('Compilation Failure')

        _, token_tree = result
        return token_tree

    @abstractmethod
    def __str__(self) -> str:
        pass


class ConfigElementExecuter(ConfigExecuter):
    def __init__(
        self,
        executer_type: str,
        data: str,
        label: str = '',
    ):
        self.executer_type = executer_type
        self.element: str = data
        self.label: str = label

    def analyze(
        self,
        tokens: List[str],
        label2executer: Dict[str, ConfigExecuter],
    ) -> Optional[Tuple[int, TokenTree]]:
        token = tokens[0]

        match = re.match(r'"(?P<keyword>.*)"', self.element)
        if match:
            keyword = match.group('keyword')
            if token != keyword:
                return None
            label = get_token_type(token)
            return 1, TokenTree(label, token)
        else:
            target_label = self.element
            if target_label in [
                'identifier',
                'integerConstant',
                'stringConstant',
                'keywordConstant',
            ]:
                token_label = get_token_type(token)
                if target_label == 'keywordConstant':
                    target_label = 'keyword'

                if token_label == target_label:
                    if target_label == 'stringConstant':
                        token = re.match(
                            r'"(?P<strConst>.*)"', token,
                        ).group('strConst')

                    return 1, TokenTree(token_label, token)
                return None

            executer = label2executer[target_label]
            return executer.analyze(tokens, label2executer)

    def __str__(self):
        executer_type_str = f'{self.element}'
        executer_label_str = f'({self.label})' if self.label else ''
        return f'({executer_type_str}{executer_label_str})'


class ConfigSequentialExecuter(ConfigExecuter):
    def __init__(
        self,
        executer_type: str,
        data: Union[List[ConfigExecuter], str],
        label: str = '',
    ):
        self.executer_type = executer_type
        self.executers: Union[List[ConfigExecuter], str] = data
        self.label: str = label

    def analyze(
        self,
        tokens: List[str],
        label2executer: Dict[str, ConfigExecuter],
    ) -> Optional[Tuple[int, TokenTree]]:
        start = 0
        nodes = []

        i = 0
        while i < len(self.executers):
            executer = self.executers[i]
            repeat_pattern = ''
            if i + 1 < len(self.executers):
                if isinstance(self.executers[i + 1], str):
                    repeat_pattern = self.executers[i + 1]
                    i += 1
            i += 1
            while True:
                result = executer.analyze(tokens[start:], label2executer)
                if not result:
                    if repeat_pattern in set(['?', '*']):
                        break
                    return None
                end, data = result
                start += end
                nodes.append(data)
                if repeat_pattern in set(['', '?']):
                    break

        token_tree = TokenTree(self.label, nodes)
        return start, token_tree

    def __str__(self):
        executers_str = ",".join([str(e) for e in self.executers])
        executer_type_str = f'{self.executer_type}'
        executer_label_str = f'({self.label})' if self.label else ''
        return f'({executer_type_str}{executer_label_str}: {executers_str})'


class ConfigChoiceExecuter(ConfigExecuter):
    def __init__(
        self,
        executer_type: str,
        data: List[ConfigExecuter],
        label: str = '',
    ):
        self.executer_type = executer_type
        self.executers: List[ConfigExecuter] = data
        self.label: str = label

    def analyze(
        self,
        tokens: List[str],
        label2executer: Dict[str, ConfigExecuter],
    ) -> Optional[Tuple[int, TokenTree]]:
        for executer in self.executers:
            result = executer.analyze(tokens, label2executer)
            if not result:
                continue

            end, node = result
            token_tree = TokenTree(self.label, [node])
            return end, token_tree

        return None

    def __str__(self):
        executers_str = ",".join([str(e) for e in self.executers])
        executer_type_str = f'{self.executer_type}'
        executer_label_str = f'({self.label})' if self.label else ''
        return f'({executer_type_str}{executer_label_str}: {executers_str})'
