"""
generate mermaid code that represent the inheritance of classes
defined in a given module

Check https://github.com/mgaitan/sphinxcontrib-mermaid/issues/5

Original code by Zulko: https://gist.github.com/Zulko/e0910cac1b27bcc3a1e6585eaee60121

"""
from __future__ import print_function
import inspect
from sphinx.util import import_object

def class_name(cls):
    """Return a string representing the class"""
    # NOTE: can be changed to str(class) for more complete class info
    return cls.__name__


class ClassDiagram(object):

    def __init__(self, module_path, base_module=None):

        self.module = import_object(module_path)
        self.base_module = base_module or self.module.__name__
        self.module_classes = set()
        self.inheritances = []
        self._populate_tree()

    def _inspect_class(self, cls):
        if not inspect.isclass(cls):
            return

        cls_name = class_name(cls)
        if (cls_name not in self.module_classes and
            cls.__module__.startswith(self.base_module)):
                self.module_classes.add(cls_name)
                for base in cls.__bases__:
                    if class_name(base) == 'object':
                        continue
                    self.inheritances.append((class_name(base), cls_name))
                    self._inspect_class(base)

    def _populate_tree(self):
        for obj in self.module.__dict__.values():
            self._inspect_class(obj)

    def __str__(self):
        return "graph TD;\n" + "\n".join(
            list(self.module_classes) + [
                "%s --> %s" % (a, b)
                for a, b in self.inheritances
            ]
        )

if __name__ == "__main__":
    print(ClassDiagram('sphinx.util', 'sphinx'))
