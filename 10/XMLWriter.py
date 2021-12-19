from __future__ import annotations
from TokenTree import TokenTree
import html


class XMLWriter:
    def __init__(self):
        self.reduction_labels = set([
            'type',
            'statement',
            'subroutineCall',
            'op',
            'unaryOp',
            'keywordConstant',
        ])

    def get_xml_content(
        self,
        token_tree: TokenTree,
        depth: int = 0,
    ):
        spacer = "".join(["  " for _ in range(depth)])

        label = token_tree.label
        lines = []
        if label in self.reduction_labels:
            for node in token_tree.nodes:
                lines += self.get_xml_content(node, depth)
            return lines

        if token_tree.single_token:
            token = html.escape(token_tree.single_token)
            lines.append(
                f'{spacer}<{label}> {token} </{label}>')
        else:
            lines.append(f'{spacer}<{label}>')
            for node in token_tree.nodes:
                lines += self.get_xml_content(node, depth + 1)
            lines.append(f'{spacer}</{label}>')

        return lines

    def write_xml(
        self,
        token_tree: TokenTree,
        output_path: str,
    ):
        content = '\n'.join(self.get_xml_content(token_tree))
        with open(output_path, 'w') as f:
            f.write(content + '\n')
