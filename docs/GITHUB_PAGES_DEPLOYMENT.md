# GitHub Pages deployment

The showcase is ready to serve directly from `docs/`. Deployment has not been confirmed. Python, Streamlit, Joblib and XGBoost run separately; the Pages interface preview never produces predictions.

## Activate the site

1. Review and push the prepared changes to `main` (`git push origin main` once ready).
2. Open [MEK-0/NACA-0012-Airfoil-Noise-Prediction](https://github.com/MEK-0/NACA-0012-Airfoil-Noise-Prediction).
3. Open **Settings**.
4. Choose **Pages** in the sidebar.
5. Under **Build and deployment**, set **Source → Deploy from a branch**.
6. Set **Branch → main**.
7. Set **Folder → /docs**.
8. Click **Save**.
9. Wait for the GitHub Pages deployment to finish; inspect the repository’s **Actions** tab and Pages status. Allow several minutes.
10. Visit **https://mek-0.github.io/NACA-0012-Airfoil-Noise-Prediction/**.

Repository admin or maintainer access is needed to configure Pages. See [GitHub’s official publishing-source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Local checks

Open `docs/index.html` directly or run, from the repository root:

```bash
python -m http.server 8000 --directory docs
```

Visit `http://127.0.0.1:8000/`. The server is only for local preview; it is not part of the deployed site. CSS, JavaScript, favicon and figures use `./` relative paths. Navigation uses same-document anchors. There are no web fonts, CDNs, package installs, fetch requests or runtime model downloads. `.nojekyll` tells Pages to serve the static files without Jekyll processing.

To check repository-subpath resolution locally, copy `docs/` into a temporary directory named `NACA-0012-Airfoil-Noise-Prediction` under a local server root and visit that subdirectory. Run `python scripts/check_docs.py` to verify references before publishing.

## Troubleshooting

| Symptom | Check / remedy |
| --- | --- |
| 404 | Confirm the successful deployment is from `main` and `/docs`, and use the full case-sensitive repository URL above. |
| CSS or images missing | Ensure `styles.css`, `script.js` and `assets/` are committed under `docs/`. Keep links relative (`./assets/...`), not domain-root paths (`/assets/...`). Check filename case and browser network errors. |
| Pages disabled or no branch selector | Check repository permissions, account/organization Pages policy and plan support for the repository visibility. Push the branch first. |
| Deployment delayed | Wait several minutes, inspect the Pages workflow in Actions, and review failed-job logs before retrying. |
| Missing index | Confirm `docs/index.html` exists on the published branch with exactly that spelling and case. |
| Old version displayed | Confirm the published commit in Actions, then refresh with cache bypass. |
| Markdown audit opens as text or downloads | This is expected with `.nojekyll`; these are source documentation files, while `index.html` is the rendered website. |
| Preview does not calculate noise | Intended: it is a clearly labeled UI preview. Run Streamlit locally or deploy Python separately for real inference. |

## After activation

Check desktop, tablet and mobile layouts, English/German switching, keyboard navigation, number-field labels, image links and footer links at the public repository-subpath URL. Confirm the preview is clearly labeled and never shows a numerical prediction. Only describe the site as live after a successful deployment and a public URL check.
