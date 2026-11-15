# Draw class inheritance diagrams

`autoclasstree` generates a class diagram from importable Python classes or
modules:

```rst
.. autoclasstree:: sphinx.errors.ConfigError sphinx.errors.ExtensionError
   :full:
```

```{eval-rst}
.. autoclasstree:: sphinx.errors.ConfigError sphinx.errors.ExtensionError
   :full:
```

Give a module to include every class it defines or imports:

```rst
.. autoclasstree:: sphinx.errors
```

Classes named directly, and every class of a `:strict:` module, appear even
when they have no base classes. Other module members appear only when they
inherit from something in the diagram.

Options:

- `:full:` shows each class's complete hierarchy.
- `:links:` makes each class a link to its documentation. Classes are looked
  up in the Python domain (for example, pages written with `sphinx.ext.autodoc`)
  and then through `sphinx.ext.intersphinx`; classes that aren't documented
  anywhere stay plain. Links only apply to HTML output.
- `:namespace: <value>` limits base classes to that namespace.
- `:strict:` includes only classes defined in the given module.

`autoclasstree` also accepts every [per-diagram option](configuration.md#per-diagram-options).
