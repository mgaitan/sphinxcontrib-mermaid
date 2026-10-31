# Build PDFs and static images

Builders other than HTML (LaTeX, texinfo) render diagrams with
[mermaid-cli](https://github.com/mermaid-js/mermaid-cli). HTML can use it too,
with `mermaid_output_format = "png"` or `"svg"`; static output adds no
JavaScript to the page.

Install the CLI:

```sh
npm install -g @mermaid-js/mermaid-cli
```

Relevant settings: `mermaid_cmd`, `mermaid_cmd_shell`, `mermaid_params`,
`mermaid_pdfcrop`, `mermaid_verbose`, and `mermaid_sequence_config`. See the
[configuration reference](configuration.md#static-output). `mermaid_config` is
passed to the CLI as a config file, and `width`/`height` options apply to the
generated image.

## Read the Docs

mermaid-cli needs a headless Chrome. On Read the Docs:

1. Install the CLI in `.readthedocs.yaml`:

   ```yaml
   version: 2
   build:
     os: ubuntu-24.04
     apt_packages:
       - libasound2t64
     tools:
       python: "3"
       nodejs: "22"
     jobs:
       post_install:
         - npm install -g @mermaid-js/mermaid-cli
   sphinx:
     configuration: docs/conf.py
   formats:
     - pdf
   python:
     install:
       - requirements: docs/requirements.txt
   ```

1. Add `docs/puppeteer-config.json`:

   ```json
   {"args": ["--no-sandbox"]}
   ```

1. In `conf.py`:

   ```python
   mermaid_params = ["-p", "puppeteer-config.json"]
   ```
