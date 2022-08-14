import ast
from typing import Any

import pytest

from deep_ast import DeepVisitor
from tests.examples.classes import Child, Foo


def test_single_method():

    expected_parent_nodes = ["Foo.method_a()"]
    expected_nodes = [
        "Module",
        "FunctionDef",
        "arguments",
        "arg",
        "Expr",
        "Call",
        "Name",
        "Load",
        "Constant",
    ]

    v = DeepVisitor()

    example_class = Foo()

    v.deep_visit(example_class.method_a)

    assert v.visited_nodes == len(expected_nodes)
    assert v.parent_nodes == expected_parent_nodes
    assert v.raw_nodes == expected_nodes


def test_nested_method():

    expected_parent_nodes = ["Foo.method_b()", "Foo.method_a()"]
    expected_nodes = [
        "Module",
        "FunctionDef",
        "arguments",
        "arg",
        "Expr",
        "Call",
        "Module",
        "FunctionDef",
        "arguments",
        "arg",
        "Expr",
        "Call",
        "Name",
        "Load",
        "Constant",
        "Attribute",
        "Name",
        "Load",
        "Load",
    ]

    v = DeepVisitor()

    example_class = Foo()

    v.deep_visit(example_class.method_b)

    assert v.visited_nodes == len(expected_nodes)
    assert v.parent_nodes == expected_parent_nodes
    assert v.raw_nodes == expected_nodes


@pytest.mark.xfail(strict=True)
def test_multiple_objects():

    expected_parent_nodes = ["Foo.method_c()", "Bar.init()", "Bar.bazz()"]
    expected_nodes = [
        "Module",
        "FunctionDef",
        "arguments",
        "arg",
        "Assign",
        "Name",
        "Store",
        "Call",
        "Module",
        "ClassDef",
        "FunctionDef",
        "arguments",
        "arg",
        "Expr",
        "Call",
        "Name",
        "Load",
        "Constant",
        "Name",
        "Load",
        "Expr",
        "Call",
        "Module",
        "FunctionDef",
        "arguments",
        "arg",
        "Expr",
        "Call",
        "Name",
        "Load",
        "Constant",
        "Attribute",
        "Name",
        "Load",
        "Load",
    ]

    v = DeepVisitor()

    example_class = Foo()

    v.deep_visit(example_class.method_c)

    assert v.visited_nodes == len(expected_nodes)
    assert v.parent_nodes == expected_parent_nodes
    assert v.raw_nodes == expected_nodes


def test_super():

    expected_parent_nodes = ["Child.example_a()", "Parent.example_a()"]

    v = DeepVisitor()

    v.deep_visit(Child.example_a)

    assert v.parent_nodes == expected_parent_nodes


class WalkClasses(DeepVisitor):
    def __init__(self) -> None:
        self.class_parents = []
        super().__init__()

    def add_class(self, class_name: str):
        if class_name not in self.class_parents:
            self.class_parents.append(class_name)

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:

        self.add_class(node.name)

        for parent_node in node.bases:

            parent_class_name = (
                parent_node.attr
                if isinstance(parent_node, ast.Attribute)
                else parent_node.id
            )

            self.add_class(parent_class_name)

            parent_node = self._find_ast_node(parent_class_name)

            if parent_node is None:
                continue

            self.visit(parent_node)

        # return self.generic_visit(node)


def test_inheritance():

    expected_parents = ["Child", "Parent", "Human"]

    expected_raw_nodes = [
        "Module",
        "ClassDef",
        "Module",
        "ClassDef",
        "Module",
        "ClassDef",
    ]

    v = WalkClasses()

    v.deep_visit(Child)

    assert v.class_parents == expected_parents
    assert v.raw_nodes == expected_raw_nodes
