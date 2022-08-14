<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Python][python-shield]][pypi-url]
[![Latest][version-shield]][pypi-url]
[![Tests][test-shield]][test-url]
[![Coverage][codecov-shield]][codecov-url]
[![License][license-shield]][license-url]
<!-- [![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url] -->

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <!-- <a href="https://github.com/DontShaveTheYak/deep-ast">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a> -->

  <h3 align="center">Deep-AST</h3>

  <p align="center">
    Parse the AST for any <a href=https://docs.python.org/3/library/ast.html#ast.Call>Call</a> nodes encountered.
    <!-- <br />
    <a href="https://github.com/DontShaveTheYak/deep-ast"><strong>Explore the docs »</strong></a>
    <br /> -->
    <br />
    <!-- <a href="https://github.com/DontShaveTheYak/deep-ast">View Demo</a>
    · -->
    <a href="https://github.com/DontShaveTheYak/deep-ast/issues">Report Bug</a>
    ·
    <a href="https://github.com/DontShaveTheYak/deep-ast/issues">Request Feature</a>
    ·
    <!-- <a href="https://la-tech.co/post/hypermodern-cloudformation/getting-started/">Guide</a> -->
  </p>
</p>

## About The Project

<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com) -->

`deep-ast` is a Python library that attempts to parse all AST that would be encountered when invoking a callable in python. It does this by extending the [ast.NodeVistor](https://docs.python.org/3/library/ast.html#ast.NodeVisitor) and [ast.NodeTransformer](https://docs.python.org/3/library/ast.html#ast.NodeTransformer) classes, so that when an [ast.Call](https://docs.python.org/3/library/ast.html#ast.Call) node is encountered, it's source code is parsed into an [ast.Node](https://docs.python.org/3/library/ast.html#ast.Call) and then passes the node to the [visit()](https://docs.python.org/3/library/ast.html#ast.NodeVisitor.visit) method.

We say attempts because currently there are some limitations. It cant parse any arbitrary code like `exec('rorrEeulaV esiar'[::-1])` which raises a ValueError, functions that aren't written in Python and all python internals like `print()`.

If you have a way around these limitations then a PR would be greatly appreciated.

## Getting Started

### Prerequisites

`deep-ast` requires python >= 3.7

### Installation

`deep-ast` is available as an easy to install pip package.
```sh
pip install deep-ast
```

## Usage

deep-ast offers drop in replacements for the [ast.NodeVistor](https://docs.python.org/3/library/ast.html#ast.NodeVisitor) and [ast.NodeTransformer](https://docs.python.org/3/library/ast.html#ast.NodeTransformer) classes.

```sh
from deep_ast import DeepVisitor, DeepTransformer
```

To start the deep processing you the `deep_visit()` method. Each function takes an optional `module` arugment. This is used if the function/method is not defined in the same file that you calling `deep_visit()` method in.

### Example to get all exceptions

This example shows how you might deeply parse the AST to
get all exceptions that might be thrown.

```python3
# Custom NodeVisitor to visit Raise nodes and record them
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

        exception_obj = node.exc

        if isinstance(exception_obj, (ast.Call, ast.Name):
            name = (
                exception_obj.id
                if isinstance(exception_obj, ast.Name)
                else exception_obj.func.id
            )

            self._add_exception(name)
            return self.generic_visit(node)

        self._add_exception("EmptyRaise")
        return self.generic_visit(node)

# Test functions to visit
def foo():
    bar()
    raise TypeError()


def bar():
    raise ValueError()

parser = ParseExceptions()

parser.deep_visit(foo)

print(parser.found_exceptions) # prints ['ValueError', 'TypeError']
```

## Roadmap

- Parsing of deeply nested attribute calls like `foo().bar().bazz()`

- Tracking of variable assignment:
  ```python3
  print_func = print
  print_func()
  ```

See the [open issues](https://github.com/DontShaveTheYak/deep-ast/issues) for a list of proposed features (and known issues).

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

This project uses poetry to manage dependencies and pre-commit to run formatting, linting and tests. You will need to have both installed to your system as well as python 3.9.

1. Fork the Project
2. Setup the environment.  
   This project uses vscode devcontainer to provide a completly configured development environment. If you are using vscode and have the remote container extension installed, you should be asked to use the devcontainer when you open this project inside of vscode.

   If you are not using devcontainers then you will need to have python installed. Install the `poetry`, `nox`, `nox_poetry` and `pre-commit` packages. Then run `poetry install` and `pre-commit install` commands. 

   Most of the steps can be found in the [Dockerfile](.devcontainer/Dockerfile).
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- ## License

Distributed under the Apache-2.0 License. See [LICENSE.txt](./LICENSE.txt) for more information. -->

## Contact

Levi - [@shady_cuz](https://twitter.com/shady_cuz)

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* Stackoverflow for getting me started [down this road](https://stackoverflow.com/questions/32560116/how-to-list-all-exceptions-a-function-could-raise-in-python-3).
* @sethmlarson for asking me which [exceptions](https://github.com/urllib3/urllib3/issues/2648) can be raised.

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[python-shield]: https://img.shields.io/pypi/pyversions/deep-ast?style=for-the-badge
[version-shield]: https://img.shields.io/pypi/v/deep-ast?label=latest&style=for-the-badge
[pypi-url]: https://pypi.org/project/deep-ast/
[test-shield]: https://img.shields.io/github/workflow/status/DontShaveTheYak/deep-ast/Tests?label=Tests&style=for-the-badge
[test-url]: https://github.com/DontShaveTheYak/deep-ast/actions?query=workflow%3ATests+branch%3Amaster
[codecov-shield]: https://img.shields.io/codecov/c/gh/DontShaveTheYak/deep-ast/master?color=green&style=for-the-badge&token=bfF18q99Fl
[codecov-url]: https://codecov.io/gh/DontShaveTheYak/deep-ast
[contributors-shield]: https://img.shields.io/github/contributors/DontShaveTheYak/deep-ast.svg?style=for-the-badge
[contributors-url]: https://github.com/DontShaveTheYak/deep-ast/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/DontShaveTheYak/deep-ast.svg?style=for-the-badge
[forks-url]: https://github.com/DontShaveTheYak/deep-ast/network/members
[stars-shield]: https://img.shields.io/github/stars/DontShaveTheYak/deep-ast.svg?style=for-the-badge
[stars-url]: https://github.com/DontShaveTheYak/deep-ast/stargazers
[issues-shield]: https://img.shields.io/github/issues/DontShaveTheYak/deep-ast.svg?style=for-the-badge
[issues-url]: https://github.com/DontShaveTheYak/deep-ast/issues
[license-shield]: https://img.shields.io/github/license/DontShaveTheYak/deep-ast.svg?style=for-the-badge
[license-url]: https://github.com/DontShaveTheYak/deep-ast/blob/master/LICENSE.txt
[product-screenshot]: images/screenshot.png
