import ast

from ._mixin import DeepMixin


class DeepVisitor(DeepMixin, ast.NodeVisitor):
    pass


class DeepTransformer(DeepMixin, ast.NodeTransformer):
    pass
