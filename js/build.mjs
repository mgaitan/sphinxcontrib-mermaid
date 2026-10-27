import { build } from "esbuild";
import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";

const outdir = "../sphinxcontrib/mermaid/_static/sphinxcontrib-mermaid";
const VENDORED = [
  { pkg: "mermaid", name: "mermaid", key: "mermaid" },
  { pkg: "@mermaid-js/mermaid-zenuml", name: "mermaid-zenuml", key: "zenuml" },
  {
    pkg: "@mermaid-js/layout-tidy-tree",
    name: "mermaid-layout-tidy-tree",
    key: "tidyTree",
  },
];

await rm(outdir, { recursive: true, force: true });
await mkdir(`${outdir}/licenses`, { recursive: true });
await build({
  entryPoints: { "sphinxcontrib-mermaid": "src/ts/index.ts" },
  outdir,
  bundle: true,
  minify: true,
  format: "esm",
  target: "es2022",
});
await cp("src/css/index.css", `${outdir}/sphinxcontrib-mermaid.css`);

const versions = {};
for (const { pkg, name, key } of VENDORED) {
  const root = `node_modules/${pkg}`;
  const dist = `${root}/dist`;
  const entry = `${name}.esm.min.mjs`;
  await mkdir(`${outdir}/${name}/chunks`, { recursive: true });
  await cp(`${dist}/${entry}`, `${outdir}/${name}/${entry}`);
  await cp(
    `${dist}/chunks/${name}.esm.min`,
    `${outdir}/${name}/chunks/${name}.esm.min`,
    { recursive: true, filter: (src) => !src.endsWith(".map") },
  );
  await cp(`${root}/LICENSE`, `${outdir}/licenses/${name}-LICENSE`);
  versions[key] = JSON.parse(await readFile(`${root}/package.json`)).version;
}
await writeFile(`${outdir}/versions.json`, JSON.stringify(versions));
