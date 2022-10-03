import ast
import sys
from http.client import HTTPConnection

import pytest

from deep_ast import DeepVisitor


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


@pytest.mark.skipif(
    sys.version_info != (3, 9),
    reason="The number of nodes visitied varies between python versions?",
)
def test_exceptions():

    parser = ParseExceptions()

    parser.deep_visit(HTTPConnection.getresponse)

    assert parser.visited_nodes == 24489
    assert len(parser.raw_exceptions) == 181
    assert len(parser.found_exceptions) == 8
    assert parser.parent_nodes[0] == "HTTPConnection.getresponse()"
    assert parser.parent_nodes[-1] == "HTTPResponse._close_conn()"
