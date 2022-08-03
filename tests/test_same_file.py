import http
import pytest
import ast

from deep_ast import DeepVisitor
from tests.examples.functions import func_a, func_b, func_d
from tests.examples.methods import Foo

from http.client import HTTPConnection
import http.client


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

    v.process_function(func_a)

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

    v.process_function(func_b)

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

    v.process_function(func_d)

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

    example_class = Foo()

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

    example_class = Foo()

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

    example_class = Foo()

    v.process_method(example_class.method_c)

    assert v.visited_nodes == len(expected_nodes)
    assert v.parent_nodes == expected_parent_nodes
    assert v.raw_nodes == expected_nodes


def test_example():

    v = DeepVisitor()

    v.process_method(HTTPConnection.getresponse, module=http.client)

    print(v.visited_nodes)
    print(v.parent_nodes)
    assert v.visited_nodes == 24489
    assert v.parent_nodes[0] == "HTTPConnection.getresponse()"
    assert v.parent_nodes[-1] == "HTTPResponse._close_conn()"


class ParseExceptions(DeepVisitor):
    def __init__(self) -> None:
        self.raw_exceptions = []
        self.found_exceptions = []
        super().__init__()

    def _add_exception(self, name: str):
        self.raw_exceptions.append(name)

        if name not in self.found_exceptions:
            self.found_exceptions.append(name)

    def visit_Raise(self, node):
        # print(f"Found Raise {node.exc=}")

        exception_obj = node.exc

        if isinstance(exception_obj, (ast.Call, ast.Name)):
            name = (
                exception_obj.id
                if isinstance(exception_obj, ast.Name)
                else exception_obj.func.id
            )

            # print(f"Found Exception {name}")
            self._add_exception(name)
            return self.generic_visit(node)

        # source = ast.get_source_segment()

        self._add_exception("EmptyRaise")
        return self.generic_visit(node)


def test_exceptions():

    parser = ParseExceptions()

    parser.process_method(HTTPConnection.getresponse, module=http.client)

    print(parser.visited_nodes)
    assert parser.visited_nodes == 24489
    assert len(parser.raw_exceptions) == 181
    assert len(parser.found_exceptions) == 8
