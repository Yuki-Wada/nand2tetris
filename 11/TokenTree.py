from __future__ import annotations
from typing import List, Union


class TokenTree:
    def __init__(
        self,
        label,
        data: Union[List[__class__], str],
    ):
        self.label: str = label

        self.nodes: List[TokenTree] = []
        self.single_token: str = ''
        if isinstance(data, list):
            for child in data:
                if child.label:
                    self.nodes.append(child)
                else:
                    self.nodes += child.nodes
        elif isinstance(data, str):
            self.single_token = data
        else:
            raise ValueError()
