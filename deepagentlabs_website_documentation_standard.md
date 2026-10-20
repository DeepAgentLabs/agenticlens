# DeepAgentLabs Package Website & Documentation Standard

Hi Team,

Every DeepAgentLabs package needs two website sections: a product landing page and a detailed documentation site. Use AgenticLens as the reference for structure, not for content.

Each intern owns the landing page and complete documentation for their assigned package. Everything below applies to every package unless the package-specific notes say otherwise.

## Packages and URLs

GitHub Pages serves each repository at `deepagentlabs.io/<repository-name>/`, so the URL path always equals the repository name. Confirm your repository name matches the table before you start.

**Where the content lives:** the URLs are on `deepagentlabs.io`, but all landing-page and documentation source lives in each package's own repository. The landing-page files, `docs/` folder, `mkdocs.yml`, and `docs.yml` workflow all belong in the package repository, for example `agenticlens`. GitHub Pages publishes them from there to `deepagentlabs.io/<repository-name>/`. Do not add or edit package content in the `deepagentlabs.github.io` repository; it only hosts the main `deepagentlabs.io` site and the custom domain.

| Package | Repository | Landing page | Documentation |
| :--- | :--- | :--- | :--- |
| **AgenticLens** *(reference)* | `agenticlens` | `deepagentlabs.io/agenticlens/` | `deepagentlabs.io/agenticlens/docs/` |
| **Agentic Chaos** | `agentic-chaos` | `deepagentlabs.io/agentic-chaos/` | `deepagentlabs.io/agentic-chaos/docs/` |
| **Agentic Sidecar** | `agentic-sidecar` | `deepagentlabs.io/agentic-sidecar/` | `deepagentlabs.io/agentic-sidecar/docs/` |
| **Agentic Evals** | `agentic-evals` | `deepagentlabs.io/agentic-evals/` | `deepagentlabs.io/agentic-evals/docs/` |
| **MCP Server** | `deep-agentic-core-mcp` | `deepagentlabs.io/deep-agentic-core-mcp/` | `deepagentlabs.io/deep-agentic-core-mcp/docs/` |
| **AgenticOps Control Tower** | `agenticops-control-tower` | `deepagentlabs.io/agenticops-control-tower/` | `deepagentlabs.io/agenticops-control-tower/docs/` |

---

## 1. Product landing page

A visitor should understand the package within approximately two minutes. Reference: `deepagentlabs.io/agenticlens/`.

### The landing page should include:
- Package name, tagline, and maturity status
- What the package does and the problem it solves
- Four to six major implemented capabilities
- A simple architecture or workflow diagram
- Installation command and minimal quick-start example
- Relevant links: Documentation, GitHub, PyPI, Examples, Contributing, and License

### Where applicable, also include:
- Supported integrations
- Example output, dashboard, report, or screenshot
- Intended users

Keep detailed configuration, API usage, CLI options, advanced examples, limitations, and troubleshooting in the documentation site. The landing page helps visitors understand and try the package quickly; the documentation teaches every capability in detail.

Landing-page files live in the root of the package repository, as in AgenticLens:

```text
package-repository/
├── index.html
├── site.css
├── site.js
└── og.png
```

The workflow copies these into the root of the deployed site, so `index.html` becomes `deepagentlabs.io/<package>/`. Never maintain a copy in the `deepagentlabs.github.io` repository.

### Link rules (important):
The site is served from a subpath, so a leading slash breaks links.
- **Use relative paths:** `href="site.css"`, `src="site.js"`, `href="docs/"`. Never `/site.css` or `/docs/`.
- **Exception:** Open Graph and Twitter image tags need the full URL, for example `https://deepagentlabs.io/agenticlens/og.png`.
- Keep `og.png` at $1200 \times 630\text{ px}$.

---

## 2. Detailed documentation

The docs must explain how to install, configure, and use every capability the package currently supports. Reference: `deepagentlabs.io/agenticlens/docs/`.

Markdown files in `docs/` build to `deepagentlabs.io/<package>/docs/`.

### Recommended structure:

```text
docs/
├── index.md
├── getting-started.md
├── architecture.md
├── features.md
├── configuration.md
├── api-reference.md     # only if the package has a Python API
├── cli-reference.md     # only if the package has a CLI
├── integrations.md
├── examples.md
├── output-formats.md    # only if the package produces reports or files
├── troubleshooting.md
├── limitations.md
└── roadmap.md
assets/
├── images/
└── diagrams/
```

MkDocs configuration and navigation go in `mkdocs.yml` at the repository root. Every page must appear in `nav`; the strict build fails otherwise.

---

## 3. Feature documentation requirements

For every implemented capability, document:
- What it does and why it is useful
- **Status:** stable or experimental
- How to enable, configure, and use it
- Required inputs and expected outputs
- A minimal working example
- Limitations or known issues

Where available, also include:
- Python API usage
- CLI usage
- Advanced examples
- Related integrations

Document planned capabilities **only** in `roadmap.md`.

### Accuracy requirements
1. Verify all documentation against the current source code and available tests.
2. Do not describe a capability as implemented unless it works today.
3. Run every command and example before committing it.
4. Keep planned capabilities in `roadmap.md`, separate from implemented capabilities.
5. Adapt and verify any material reused from another DeepAgentLabs package.
6. Show the verified package version on `docs/index.md`.

---

## 4. Standard repository structure

Every package repository uses this layout alongside its existing source code:

```text
package-repository/
├── index.html
├── site.css
├── site.js
├── og.png
├── mkdocs.yml
├── pyproject.toml       # includes a "docs" optional-dependency group
├── docs/
│   ├── index.md
│   ├── getting-started.md
│   ├── ...              # see section 2
│   └── assets/
│       ├── images/
│       └── diagrams/
└── .github/
    └── workflows/
        └── docs.yml
```

Add `site/` to `.gitignore`. It is generated by the workflow; never edit or commit it.

---

## 5. Build and deployment

One workflow builds the docs into `site/docs/`, copies the landing page into `site/`, and deploys `site/` to GitHub Pages. Pull requests build with strict checks but do not deploy.

### One-time repository settings
- [ ] **Settings $\rightarrow$ Pages $\rightarrow$ Source:** GitHub Actions (not "Deploy from a branch").
- [ ] `deepagentlabs.io` must stay configured on the `deepagentlabs.github.io` organization Pages site and be verified in the DeepAgentLabs GitHub organization settings. Package repositories inherit it from there.
- [ ] In each package repository, leave the custom-domain field empty and do not add a `CNAME` file.

### Sample `mkdocs.yml`
Replace `agenticlens` and the `nav` with your package's values.

```yaml
site_name: AgenticLens Documentation
site_url: https://deepagentlabs.io/agenticlens/docs/
repo_url: https://github.com/deepagentlabs/agenticlens
edit_uri: edit/main/docs/
docs_dir: docs

theme:
  name: material

validation:
  omitted_files: warn
  absolute_links: warn
  unrecognized_links: warn
  anchors: warn

# a page missing from nav fails the strict build
nav:
  - Home: index.md
  - Getting started: getting-started.md
  - Architecture: architecture.md
  - Features: features.md
  - Configuration: configuration.md
  - API reference: api-reference.md         # remove if not applicable
  - CLI reference: cli-reference.md         # remove if not applicable
  - Integrations: integrations.md
  - Examples: examples.md
  - Output formats: output-formats.md       # remove if not applicable
  - Troubleshooting: troubleshooting.md
  - Limitations: limitations.md
  - Roadmap: roadmap.md
```

Remove any page that does not apply from both `docs/` and `nav`. For example, if the package has no CLI, do not create `cli-reference.md` and do not list it in `nav`. A `nav` entry pointing to a missing file fails the strict build.

### Docs dependencies
Declare MkDocs and its theme as a `docs` optional-dependency group in `pyproject.toml`, as AgenticLens does. The workflow installs them with `uv sync --extra docs`.

### Deployment workflow
Copy this workflow into `.github/workflows/docs.yml` exactly as shown. It is the same workflow AgenticLens uses. It builds the docs into `site/docs/`, copies the landing-page files into `site/`, and deploys `site/` to GitHub Pages. It uses relative paths, so it works in any package repository without changes.

```yaml
name: Docs

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.12

      - name: Configure Pages
        if: github.event_name != 'pull_request'
        uses: actions/configure-pages@v6
        with:
          enablement: true

      - name: Install docs dependencies
        run: uv sync --extra docs --python 3.12

      - name: Build docs
        run: uv run mkdocs build --strict --site-dir site/docs

      - name: Add product website
        run: |
          cp index.html site/index.html
          cp site.css site/site.css
          cp site.js site/site.js
          cp og.png site/og.png
          touch site/.nojekyll

      - name: Upload artifact
        if: github.event_name != 'pull_request'
        uses: actions/upload-pages-artifact@v5
        with:
          path: site

  deploy:
    if: github.event_name != 'pull_request'
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

Do not modify the workflow in your package. If it needs a change, it will be updated here and in AgenticLens first.

### Test locally before pushing
For the docs:

```bash
uv sync --extra docs
uv run mkdocs serve
```

For the landing page, use a local web server rather than opening the file directly, because some browser features behave differently under `file://`:

```bash
python -m http.server 8000
```

Run it from the repository root, then open `http://localhost:8000/`.

---

## 6. Consistency, review, and definition of done

All packages share one look so the sites feel like one product family:
- Docs use the Material for MkDocs theme with the same colors and fonts as AgenticLens.
- Every landing page has a header link back to `deepagentlabs.io`.
- Landing pages follow the AgenticLens section order.

### A package is done when:
- [ ] The landing page loads at `deepagentlabs.io/<package>/` with no broken links, images, or styles.
- [ ] The docs load at `deepagentlabs.io/<package>/docs/` and `mkdocs build --strict` passes.
- [ ] Every implemented capability is labeled **stable** or **experimental**, and planned capabilities appear only in the roadmap.
- [ ] A reviewer other than the author has run every install command and code example successfully.
- [ ] The workflow deploys automatically on merge to `main`, with nothing committed under `site/`.

---

## 7. PyPI packages

Every package is published on PyPI. Add its PyPI link to the landing page's links, and use its install command in the landing page's installation section.

| Package | PyPI | Install command |
| :--- | :--- | :--- |
| **AgenticLens** | `agenticlens` | `pip install agenticlens` |
| **Agentic Chaos** | `agentic-chaos` | `pip install agentic-chaos` |
| **Agentic Sidecar** | `agentic-sidecar` | `pip install agentic-sidecar` |
| **Agentic Evals** | `agentic-evals` | `pip install agentic-evals` |
| **MCP Server** | `deep-agentic-core-mcp` | `pip install deep-agentic-core-mcp` |
| **AgenticOps Control Tower** | `agenticops-control-tower` | `pip install agenticops-control-tower` |

Show the current PyPI version next to the maturity status. Before publishing, run the install command in a fresh virtual environment and confirm the quick-start works with that version.