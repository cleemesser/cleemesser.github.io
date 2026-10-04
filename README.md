# CV site

A one-page academic CV generated from a single YAML file by a ~150-line Python script,
deployed to GitHub Pages by GitHub Actions.

```
content/cv.yaml        all content (edit this)
templates/index.html   Jinja2 page template
static/style.css       styles, including dark mode and print
build.py               generator: YAML -> _site/index.html
fetch_orcid.py         lists ORCID works not yet in cv.yaml
.github/workflows/     build + deploy on every push to main
```

## Local use

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python build.py --serve          # http://localhost:8000
```

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

Open the site and print (or use the footer link). The print stylesheet drops the header
figure and placeholder entries and shows link URLs.

## Before publishing

Search `cv.yaml` for `VERIFY` and `TODO`/`TITLE` placeholders.
