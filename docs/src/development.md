# Develop sphinxcontrib-mermaid

You need Python 3.10+, Node.js 22+, and pnpm.

```sh
make develop   # install Python and JavaScript dependencies
make build     # bundle the runtime and vendored Mermaid, build a wheel
make lint      # ruff, oxlint/oxfmt, mdformat, codespell
make test      # pytest and Playwright
make docs      # build these docs
```

The runtime lives in `js/src/ts` and is bundled by `js/build.mjs` into
`sphinxcontrib/mermaid/_static/sphinxcontrib-mermaid/`, together with Mermaid's
own ES module files copied from `node_modules`. Playwright tests in `js/tests`
build the site in `js/tests/site` and run against it.
