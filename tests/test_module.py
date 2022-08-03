import pytest

from deep_ast import DeepVisitor
from tests.examples import methods, functions


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

    v.process_function(functions.func_a)

    assert v.visited_nodes == len(expected_nodes)
    assert v.parent_nodes == expected_parent_nodes
    assert v.raw_nodes == expected_nodes, "Should have visited these nodes"


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

    v.process_function(functions.func_b)

    assert v.visited_nodes == len(expected_nodes)
    assert v.parent_nodes == expected_parent_nodes
    assert v.raw_nodes == expected_nodes


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

    v.process_function(functions.func_d)

    assert v.visited_nodes == len(expected_nodes)
    assert v.parent_nodes == expected_parent_nodes
    assert v.raw_nodes == expected_nodes


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

    example_class = methods.Foo()

    v.process_method(example_class.method_a)

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

    example_class = methods.Foo()

    v.process_method(example_class.method_b)

    assert v.visited_nodes == len(expected_nodes)
    assert v.parent_nodes == expected_parent_nodes
    assert v.raw_nodes == expected_nodes


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

    example_class = methods.Foo()

    v.process_method(example_class.method_c)

    assert v.visited_nodes == len(expected_nodes)
    assert v.parent_nodes == expected_parent_nodes
    assert v.raw_nodes == expected_nodes
