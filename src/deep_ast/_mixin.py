import ast
import functools
import inspect
from inspect import getmembers, getmodule, getsource, isbuiltin
from textwrap import dedent
from types import FunctionType, MethodDescriptorType, MethodType, MethodWrapperType
from typing import TYPE_CHECKING, Any, List, Optional, Union

if TYPE_CHECKING:
    _Base = ast.NodeVisitor
else:
    _Base = object


class DeepMixin(_Base):
    def __init__(self) -> None:
        self.module = None
        self.obj = None
        self.visited_nodes = 0
        self.raw_nodes: List[str] = []
        self.parent_nodes: List[str] = []
        self.last_obj: Union[None, FunctionType, MethodType, object] = None
        super().__init__()

    def deep_visit(self, callable: Union[FunctionType, MethodType]):
        """Visit all AST nodes of the passed in `callable`. This will include the AST of any [ast.Call](https://docs.python.org/3/library/ast.html#ast.Call) nodes that are encountered.

        Args:
            callable (Union[FunctionType, MethodType]): The function or method that will be "deep" visited.
        """

        start_node = None

        self.module = getmodule(callable)  # type: ignore

        parent = get_class_that_defined_method(callable)

        if parent:
            self.obj = parent
            self.last_obj = parent

        start_node = self._convert_to_ast_node(callable)

        if not start_node:
            raise Exception(f"Could not find AST node for {callable}")

        self.visit(start_node)

    def _convert_to_ast_node(
        self,
        item: Union[FunctionType, MethodType, MethodWrapperType],
        record_node: bool = True,
    ) -> Optional[ast.AST]:

        if isinstance(item, MethodWrapperType):
            # print(f"Unable to process method wrapper: {item.__name__}")
            return None

        if isinstance(item, MethodDescriptorType):
            # print(f"Unable to process method desciption: {item.__name__}")
            return None

        if record_node:
            self._record_node(item)

        try:
            source = self._get_source(item)
        except TypeError:
            # print(f"Invalid type {type(item)} for {item.__name__}")
            return None

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
        return dedent(getsource(item))

    def _module_search(self, item: str, excludes: Optional[List] = None):

        # print(f"Searching for {item}")

        if excludes is None:
            excludes = []

        for name, object in getmembers(self.module):

            if object in excludes:
                continue

            if name == item:

                # For some reason built-in exceptions
                # get pass this check.
                if isbuiltin(object):
                    print(f"Skipping built-in {name}")
                    return None

                return object

            attr = getattr(object, item, None)

            if attr is not None:

                if isbuiltin(attr):
                    print(f"Skipping built-in {name}")
                    return None

                return attr

    def _find_ast_node(self, item: str):

        item_object = self._module_search(item, [self.last_obj])

        if item_object is None:
            return item_object

        return self._convert_to_ast_node(item_object)

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
        method_name: str = node.attr

        # like self.name
        if isinstance(node.value, ast.Attribute):
            return

        # like self.speak()
        if isinstance(node.value, ast.Name):
            obj_name = node.value.id

        # like super().speak()
        if isinstance(node.value, ast.Call):

            # todo fix this
            # like foo().bar().bazz()
            if isinstance(node.value.func, ast.Attribute):
                # print("Found nested attribute")
                # print(ast.dump(node, indent=4))
                return

            method_name = node.attr
            obj_name = node.value.func.id  # type: ignore[attr-defined]

            if obj_name == "super":
                self._process_super(method_name)
                return

        # Self doesnt always mean the object we started with... We could be parsing a method on some other
        # class than which we started.
        if obj_name == "self":
            method_obj = getattr(self.last_obj, method_name, None)

            if method_obj is not None:

                method_node = self._convert_to_ast_node(method_obj)

                if not method_node:
                    print(f"Unable to find method object for {obj_name}.{method_obj}()")
                    return

                self.visit(method_node)
                return

            # Everthing below this line should not be in the "if" statement...
            # but doing so makes the problem worse. The problem is with var.foo()
            # how do you know what class "var" is so you can look up the method "foo".
            # Right now I dont know but its something I'm going to work on...

            # If method_object is None we should still search the module tree for
            # everything but the current obj and start object, this is still a bad approach
            # because there could still be duplicate objects with the same method todo list to fix

            method_node = self._find_ast_node(method_name)

            if not method_node:
                # print(f"YOLO search unable to find {method_name} in {self.module}")
                return

            self.visit(method_node)
            return

    def _get_class_def(self, item: object):
        class_node = self._convert_to_ast_node(item, record_node=False)  # type: ignore

        if class_node is None:
            raise Exception(f"Unable to get AST node for {item}")

        class_def = _find_class_def(class_node)

        if class_def is None:
            Exception(f"Failed to find ClassDef for {item}")

        return class_def

    def _process_super(self, method_name: str):

        class_def = self._get_class_def(self.last_obj)

        parent_class_names = []

        for parent in class_def.bases:
            if isinstance(parent, ast.Attribute):
                parent_class_names.append(parent.attr)
                continue

            parent_class_names.append(parent.id)

        if not parent_class_names:
            print(f"Failed to find parent classes for {method_name}")
            return

        # print(parent_class_names)

        parent_search_results = [
            self._module_search(class_name) for class_name in parent_class_names
        ]

        parent_class_objs = [
            parent_obj for parent_obj in parent_search_results if parent_obj is not None
        ]

        if not parent_class_objs:
            print(f"Failed to convert {parent_class_names} to {parent_class_objs}")

        attr_obj = None

        for parent_obj in parent_class_objs:
            attr_obj = getattr(parent_obj, method_name, None)

            if attr_obj:
                break

        if attr_obj is None:
            print(f"Failed to find {method_name} in {parent_class_objs}")
            print(f"{parent_class_objs}")
            return

        attr_node = self._convert_to_ast_node(attr_obj)

        if attr_node is None:
            return

        self.visit(attr_node)

        return

    def _proccess_name(self, node: ast.Name):
        func_name = node.id

        # There is bug for super().foo()
        # For what ever reason it seems like the attribute foo()
        # comes first in the AST and then super().
        if func_name == "super":
            return

        func_node = self._find_ast_node(func_name)

        if not func_node:
            # print(f"Unable to find {func_name} in {self.module.__name__}")
            return

        self.visit(func_node)

    def _proccess_call(self, node: ast.Call):

        if isinstance(node.func, ast.Attribute):
            self._process_attr(node.func)
            return

        if isinstance(node.func, ast.Name):
            self._proccess_name(node.func)
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
