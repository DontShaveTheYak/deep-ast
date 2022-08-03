import functools
from inspect import getsource, getmembers, isbuiltin, getmodule
import inspect
from textwrap import dedent
import ast

from typing import Any, Optional, Union
from types import FunctionType, MethodType, MethodWrapperType


class DeepMixin:
    def __init__(self) -> None:
        self.module = None
        self.obj = None
        self.last_obj = None
        self.visited_nodes = 0
        self.raw_nodes = []
        self.parent_nodes = []
        super().__init__()

    def process_function(self, function: FunctionType, module=None):
        self.module = getmodule(function) if module is None else module

        start_node = self._convert_to_ast_node(function)

        self.visit(start_node)

    def process_method(self, method: MethodType, module=None):
        self.module = getmodule(method) if module is None else module

        parent = get_class_that_defined_method(method)

        if parent is None:
            raise Exception(f"Could not find class for method {method.__name__}")

        self.obj = parent
        self.last_obj = parent

        method = getattr(parent, method.__name__)

        start_node = self._convert_to_ast_node(method)

        self.visit(start_node)

    def _convert_to_ast_node(
        self, item: Union[FunctionType, MethodType, MethodWrapperType]
    ) -> Optional[ast.AST]:

        if isinstance(item, MethodWrapperType):
            print(f"Unable to process method wrapper. {item}")
            print(dir(item))
            return None

        self._record_node(item)
        source = self._get_source(item)

        return ast.parse(source)

    def _record_node(self, item: Union[FunctionType, MethodType]):

        if isinstance(item, MethodType):
            self.last_obj = item.__self__
            self.parent_nodes.append(
                f"{item.__self__.__class__.__name__}.{item.__name__}()"
            )
            return

        if isinstance(item, FunctionType):

            parent_class = get_class_that_defined_method(item)

            if parent_class:
                self.last_obj = parent_class
                self.parent_nodes.append(f"{parent_class.__name__}.{item.__name__}()")
                return

            self.parent_nodes.append(f"{item.__name__}()")
            return

        if isinstance(item, type):
            self.parent_nodes.append(f"{item.__name__}.init()")
            return

    def _get_source(self, item: Any):

        try:
            source = dedent(getsource(item))
        except TypeError as e:
            print(self.raw_nodes[-1])
            print(self.parent_nodes[-1])
            raise Exception(f"Invalid type {type(item)} for {item.__name__}") from e
        # print(source)
        return source

    def _module_search(self, item: str):

        print(f"Searching in module for {item}")

        for name, object in getmembers(self.module):

            if object is self.last_obj:
                continue

            if name == item:

                if isbuiltin(object):
                    print(f"Skipping built-in {name}")
                    return None

                print(f"Converting func {name} with type {type(object)}")

                return self._convert_to_ast_node(object)

            attr = getattr(object, item, None)

            if attr is not None:

                if isbuiltin(attr):
                    print(f"Skipping built-in {name}")
                    return None

                print(
                    f"Converting attr {item=} {attr=} {object=} with type {type(attr)}"
                )

                return self._convert_to_ast_node(attr)

    def visit(self, node: ast.AST) -> Any:

        self.visited_nodes += 1

        self.raw_nodes.append(node.__class__.__name__)

        if isinstance(node, ast.Call):
            self._proccess_call(node)

        # if isinstance(node, ast.ClassDef):
        #     self._process_class_def(node)

        return super().visit(node)

    def _process_attr(self, node: ast.Attribute):

        obj_name: Optional[str] = None
        method_name: Optional[str] = None

        # like self.speak()
        if isinstance(node.value, ast.Attribute):
            obj_name = node.value.value.id
            method_name = node.attr

        if isinstance(node.value, ast.Name):
            method_name = node.attr
            obj_name = node.value.id

        # like super().speak()
        if isinstance(node.value, ast.Call):
            method_name = node.attr
            obj_name = node.value.func.id

        print(f"!!!!!!!1 {obj_name=} {method_name=}")

        # if obj_name == "super":
        #     self._process_super(method_name)
        #     return

        # Self doesnt always mean the object we started with... We could be parsing a method on some other
        # class than which we started.
        if obj_name == "self":
            method_obj = getattr(self.last_obj, method_name, None)

            if method_obj is not None:

                print(f"Converting attr222 {method_name} with type {type(method_obj)}")

                method_node = self._convert_to_ast_node(method_obj)

                if not method_node:
                    print(f"Unable to find method object for {obj_name}.{method_obj}()")
                    return

                self.visit(method_node)
                return

            print(f"GELPPLPD {method_name}")

            # If method_object is None we should still search the module tree for
            # everything but the current obj and start object, this is still a bad approach
            # because there could still be duplicate objects with the same method todo list to fix

            method_node = self._module_search(method_name)

            if not method_node:
                # print(f"YOLO search unable to find {method_name} in {self.module}")
                return

            self.visit(method_node)
            return

    # def _visit_once(self, node):
    #     """Visit a node."""
    #     method = "visit_" + node.__class__.__name__
    #     visitor = getattr(self, method, None)

    #     if visitor is None:
    #         return
    #     return visitor(node)

    def _process_super(self, method_name: str):

        class_node = self._convert_to_ast_node(self.last_obj)

        class_def = _find_class_def(class_node)

        if class_def is None:
            Exception(f"Failed to find ClassDef for {self.last_obj}")

        parent_class_names = [parent.id for parent in class_def.bases]

        parent_search_results = [
            self._module_search(class_name) for class_name in parent_class_names
        ]

        parent_class_objs = [
            parent_obj for parent_obj in parent_search_results if parent_obj is not None
        ]

        # for child_node in ast.iter_child_nodes(node):
        #     print(f"BNOUS {child_node.__class__.__name__}")
        #     # print(child_node.id)
        #     # print(self.raw_nodes[-1])

        # raise Exception(parent_class_objs, method_name)

    def _proccess_name(self, node: ast.Name):
        func_name = node.func.id
        print(f"Function {func_name}")

        # if func_name == "super":
        #     self._process_super(node.func)
        #     return

        func_node = self._module_search(func_name)

        if not func_node:
            print(f"Unable to find {func_name} in {self.module.__name__}")
            return

        self.visit(func_node)

    def _proccess_call(self, node: ast.Call):

        print(f"Processing call {node.func}")

        if isinstance(node.func, ast.Attribute):

            self._process_attr(node.func)
            return

        if isinstance(node.func, ast.Name):
            self._proccess_name(node)
            return


def _find_class_def(start_node: ast.AST):
    for node in ast.walk(start_node):
        if isinstance(node, ast.ClassDef):
            return node


# Thanks Stackoverflow! https://stackoverflow.com/a/25959545/3888850
def get_class_that_defined_method(meth):
    if isinstance(meth, functools.partial):
        return get_class_that_defined_method(meth.func)
    if inspect.ismethod(meth) or (
        inspect.isbuiltin(meth)
        and getattr(meth, "__self__", None) is not None
        and getattr(meth.__self__, "__class__", None)
    ):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls
        meth = getattr(meth, "__func__", meth)  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(
            inspect.getmodule(meth),
            meth.__qualname__.split(".<locals>", 1)[0].rsplit(".", 1)[0],
            None,
        )
        if isinstance(cls, type):
            return cls
    return getattr(meth, "__objclass__", None)  # handle special descriptor objects
