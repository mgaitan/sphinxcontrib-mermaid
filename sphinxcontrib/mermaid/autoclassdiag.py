import inspect
import sys
from collections.abc import Iterator
from typing import Any

from sphinx.errors import ExtensionError
from sphinx.util import import_object

from .exceptions import MermaidError


def get_classes(*cls_or_modules: str, strict: bool = False) -> Iterator[type[Any]]:
    """
    given one or several fully qualified names, yield class instances found.

    If ``strict`` is only consider classes that are strictly defined in that module
    and not imported from somewhere else.
    """
    for cls_or_module in cls_or_modules:
        try:
            obj = import_object(cls_or_module)
        except ExtensionError as e:
            raise MermaidError(str(e))

        if inspect.isclass(obj):
            yield obj

        elif inspect.ismodule(obj):
            for obj_ in obj.__dict__.values():
                if inspect.isclass(obj_) and (not strict or obj_.__module__.startswith(obj.__name__)):
                    yield obj_
        else:
            raise MermaidError(f"{cls_or_module} is not a class nor a module")


def class_graph(
    *cls_or_modules: str, full: bool = False, strict: bool = False, namespace: str | None = None
) -> tuple[dict[str, type[Any]], set[tuple[str, str]]]:
    """
    Return the classes to draw, by name, and the ``(base, subclass)`` name pairs between them.

    Classes named directly, and module members under ``strict``, are kept even without bases.
    """
    classes: dict[str, type[Any]] = {}
    inheritances: set[tuple[str, str]] = set()

    def get_tree(cls: type[Any]) -> None:
        for base in cls.__bases__:
            if base.__name__ == "object":
                continue
            if namespace and not base.__module__.startswith(namespace):
                continue
            classes.setdefault(base.__name__, base)
            classes.setdefault(cls.__name__, cls)
            inheritances.add((base.__name__, cls.__name__))
            if full:
                get_tree(base)

    for cls_or_module in cls_or_modules:
        for cls in get_classes(cls_or_module, strict=strict):
            if strict or cls_or_module not in sys.modules:
                classes.setdefault(cls.__name__, cls)
            get_tree(cls)

    return classes, inheritances


def format_class_diagram(classes: dict[str, type[Any]], inheritances: set[tuple[str, str]]) -> str:
    if not classes:
        return ""
    related = {name for pair in inheritances for name in pair}
    lines = [f"  class {name}" for name in sorted(classes) if name not in related]
    lines += [f"  {a} <|-- {b}" for a, b in sorted(inheritances)]
    return "classDiagram\n" + "\n".join(lines)


def class_diagram(*cls_or_modules: str, full: bool = False, strict: bool = False, namespace: str | None = None) -> str:
    return format_class_diagram(*class_graph(*cls_or_modules, full=full, strict=strict, namespace=namespace))


if __name__ == "__main__":

    class A:
        pass

    class B(A):
        pass

    class C1(B):
        pass

    class C2(B):
        pass

    class D(C1, C2):
        pass

    class E(C1):
        pass

    print(class_diagram("__main__.D", "__main__.E", full=True))
