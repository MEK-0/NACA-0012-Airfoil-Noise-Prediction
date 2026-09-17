# Validation record

## Academic archive redesign — 2026-09-18

- Replaced the showcase layout with an 880px academic report, Arial typography, blue underlined links, plain tables, horizontal rules and an original monochrome wing SVG.
- `python scripts/check_docs.py`: passed; 20 local references, 40 unique IDs, five evidence images and five labeled fields. All 128 English/German translation pairs are present. Published metrics match the unchanged evidence JSON.
- Local HTTP verification: the report and all 13 distinct resources, including the translation dictionary and wing logo, returned HTTP 200 under `/NACA-0012-Airfoil-Noise-Prediction/`.
- HTML tag nesting and closing tags checked with the standard-library HTML parser. Both JavaScript files pass `node --check`.
- A DOM harness built from the actual HTML verified every translated text and image description, repeated English/German switching, document language/title, pressed states, unchanged form values, valid/invalid messages, status clearing, reset handling and prevented submission. English HTML matches the English dictionary. These checks do not substitute for browser rendering.
- Existing chart PNGs, metrics JSON, model artifacts, datasets and notebooks remain unchanged. The Python regression suite still passes (four tests; two pre-existing feature-name warnings).
- Browser discovery again returned no connections. Actual desktop/mobile rendering and browser-native number entry remain unverified; inspect these manually before publication.
- Language changes are session-only and default to English on reload. There is no storage, network request, build step or inference in the report. English remains readable without JavaScript, with a bilingual notice explaining the language-switch requirement. Supporting Markdown documents remain in English and are labeled accordingly.

## Original showcase validation (historical)

Verified on 2026-09-18 using Python 3.12.13, scikit-learn 1.6.1 and XGBoost 3.0.2. Full figure/evaluation dependency versions are recorded in `assets/metrics.json`. Streamlit application checks used Streamlit 1.64.0.

## Checks

- `python -m pytest -q`: **4 passed**. The original three tests pass plus a holdout regression test that checks scaler statistics, split indices and both models’ published metrics. Two existing warnings remain because the original smoke tests pass unnamed NumPy arrays to a scaler fitted with named columns.
- `python -m compileall -q app src scripts tests main.py`: passed.
- `python scripts/check_docs.py`: validates all local HTML references, section anchors, unique IDs, image alternative text, labeled controls, metric consistency and relative Pages paths.
- Local HTTP check: the index and all **12 distinct local references** returned HTTP 200 beneath `/NACA-0012-Airfoil-Noise-Prediction/`, including CSS, JavaScript, figures and documentation.
- `node --check docs/script.js`: syntax passed. Node is used only as an optional development check, never for building or serving the site.
- JavaScript behavior checked with a temporary DOM-stub harness: initial labels, slider update, reset, menu toggle, Escape and focus return, closing on link activation, and prevention of form submission passed. This is not a browser layout test.
- Streamlit `AppTest`: initial render and clicking the prediction button succeeded without exceptions. Default input produced **124.09 dB XGBoost / 123.97 dB linear regression**, matching the historical screenshot. The image-width keyword was updated because the original keyword is absent in the installed Streamlit API.
- All five generated chart PNGs were visually inspected for labels, legends, clipping and correspondence to the evidence.
- Preserved data, notebook and model file bytes are checked against the original Git commit; training was not executed.

## Initial environment failures

The host initially lacked the Python dependencies. A temporary Python 3.12 environment was prepared with estimator versions matching artifact metadata. The first original test run then failed at XGBoost import because macOS OpenMP (`libomp`) was missing. Installing the runtime resolved all three import failures. These were environment failures, not changed model behavior.

Matplotlib printed font-cache permission warnings during its first import, then generated all five figures successfully using its local configuration cache. Cache and virtual-environment files are ignored and are not deployment assets.

## Browser and deployment limits

The Browser runtime reported no available browser connections; discovery returned an empty list. Therefore desktop/tablet/mobile screenshots, browser-computed overflow checks, keyboard interaction in an actual browser and JavaScript-disabled rendering were **not verified visually**. Responsive breakpoints at 1,000 and 760 pixels, a no-JavaScript visible navigation fallback, focus styles, semantic labels and reduced-motion handling are implemented and inspected in source. A manual browser pass remains recommended after deployment.

GitHub Pages settings were not changed and the public URL was not confirmed live. The expected address is https://mek-0.github.io/NACA-0012-Airfoil-Noise-Prediction/. See `GITHUB_PAGES_DEPLOYMENT.md` for activation.
