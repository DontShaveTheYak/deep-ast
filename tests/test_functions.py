import sys

import pytest

from deep_ast import DeepVisitor
from tests.examples.functions import func_a, func_b, func_d


@pytest.mark.skipif(
    sys.version_info != (3, 9),
    reason="The number of nodes visitied varies between python versions?",
)
def test_single_func():

    expected_parent_nodes = ["func_a()"]
    expected_nodes = [
        "Module",
        "FunctionDef",
        "arguments",
        "Expr",
        "Call",
        "Name",
        "Load",
        "Constant",
    ]
    v = DeepVisitor()

    v.deep_visit(func_a)

    assert v.visited_nodes == len(expected_nodes)
    assert v.parent_nodes == expected_parent_nodes
    assert v.raw_nodes == expected_nodes, "Should have visited these nodes"


@pytest.mark.skipif(
    sys.version_info != (3, 9),
    reason="The number of nodes visitied varies between python versions?",
)
def test_nested_func():

    expected_parent_nodes = ["func_b()", "func_a()"]
    expected_nodes = [
        "Module",
        "FunctionDef",
        "arguments",
        "Expr",
        "Call",
        "Module",
        "FunctionDef",
        "arguments",
        "Expr",
        "Call",
        "Name",
        "Load",
        "Constant",
        "Name",
        "Load",
    ]

    v = DeepVisitor()

    v.deep_visit(func_b)

    assert v.visited_nodes == len(expected_nodes)
    assert v.parent_nodes == expected_parent_nodes
    assert v.raw_nodes == expected_nodes


@pytest.mark.skipif(
    sys.version_info != (3, 9),
    reason="The number of nodes visitied varies between python versions?",
)
def test_continues():

    expected_parent_nodes = ["func_d()", "func_a()", "func_c()"]
    expected_nodes = [
        "Module",
        "FunctionDef",
        "arguments",
        "Expr",
        "Call",
        "Module",
        "FunctionDef",
        "arguments",
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
        "Expr",
        "Call",
        "Name",
        "Load",
        "Constant",
        "Name",
        "Load",
    ]
    v = DeepVisitor()

    v.deep_visit(func_d)

    assert v.visited_nodes == len(expected_nodes)
    assert v.parent_nodes == expected_parent_nodes
    assert v.raw_nodes == expected_nodes
