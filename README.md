# CV site

A short landing page and a full CV (HTML and LaTeX PDF), generated from a single YAML
file by a Python script and deployed to GitHub Pages by GitHub Actions.

```
/                                    landing page: links, one-paragraph summary, skills
/cv/                                 full CV (not linked from the landing page)
/cv/Christopher-Lee-Messer-CV.pdf    full CV typeset with pdflatex
```

```
content/cv.yaml        all content (edit this)
templates/landing.html landing page template
templates/cv.html      full CV page template
templates/cv.tex       LaTeX template for the PDF
static/style.css       styles, including dark mode and print
build.py               generator: YAML -> _site/
fetch_orcid.py         lists ORCID works not yet in cv.yaml
.github/workflows/     build + deploy on every push to main
```

## Local use

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python build.py --serve          # http://localhost:8000
```

The build runs `pdflatex`. Use `--no-pdf` to skip it.

## Publish on GitHub Pages

1. Create a repository (for a site at `https://USERNAME.github.io`, name it `USERNAME.github.io`;
   any other name gives `https://USERNAME.github.io/REPO`).
2. Push this folder to the `main` branch.
3. In the repository: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. Each push to `main` rebuilds and redeploys (see the Actions tab).

## Keeping publications current

`python fetch_orcid.py` queries the public ORCID API and prints YAML stubs for works that are
not yet in `cv.yaml`. Paste the ones you want into the right group and add authors.

## PDF

The build typesets `templates/cv.tex` into `_site/cv/Christopher-Lee-Messer-CV.pdf`.
The CV page links to it. Placeholder entries are left out, and links print as
short typeable URLs.

## Before publishing

Search `cv.yaml` for `VERIFY` and `TODO`/`TITLE` placeholders.
