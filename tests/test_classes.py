from tests.examples.classes import Child
from deep_ast import DeepVisitor


def test_inheritance():

    v = DeepVisitor()

    v.process_method(Child.example_a)

    print(v.raw_nodes)
    print(v.visited_nodes)
    print(v.parent_nodes)
