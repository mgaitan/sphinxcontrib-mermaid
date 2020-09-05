import inspect
from sphinx.util import import_object, ExtensionError
from .exceptions import MermaidError


def expand_namespace(*cls_or_modules):
    for cls_or_module in cls_or_modules:
        try:
            obj = import_object(cls_or_module)
        except ExtensionError as e:
            raise MermaidError(str(e))

        if inspect.isclass(obj):
            yield obj
        elif inspect.ismodule(obj):
            for obj_ in obj.__dict__.values():
                if inspect.isclass(obj_):
                    yield obj_
        else:
            raise MermaidError("%s is not an class nor a module" % cls_or_module)


def class_diagram(*cls_or_modules, full=False):
    inheritances = set()

    def get_tree(cls):
        for base in cls.__bases__:
            if base.__name__ == 'object':
                continue
            inheritances.add((base.__name__, cls.__name__))
            if full:
                get_tree(base)

    for cls in expand_namespace(*cls_or_modules):
        get_tree(cls)

    return "classDiagram\n" + "\n".join(
            "  %s <|-- %s" % (a, b)
                for a, b in inheritances
            )


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


