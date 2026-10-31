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

Options:

- `:full:` shows each class's complete hierarchy.
- `:namespace: <value>` limits base classes to that namespace.
- `:strict:` includes only classes defined in the given module.

`autoclasstree` also accepts every [per-diagram option](configuration.md#per-diagram-options).
