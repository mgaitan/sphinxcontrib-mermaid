import inspect
from sphinx.util import import_object



def class_diagram(*cls_names, full=False):
    inheritances = set()

    def get_tree(cls):
        for base in cls.__bases__:
            if base.__name__ == 'object':
                continue
            inheritances.add((base.__name__, cls.__name__))
            if full:
                get_tree(base)

    for cls_name in cls_names:

        cls = import_object(cls_name)
        if not inspect.isclass(cls):
            from .exceptions import MermaidError
            raise MermaidError("%s is not a class" % cls_name)

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


