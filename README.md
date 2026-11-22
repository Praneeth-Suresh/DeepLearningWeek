# Truthflow: multi-source news verification prototype

Truthflow was built by a Deep Learning Week hackathon team to make claims in news and social media posts easier to inspect against other sources. The prototype explored how to extract claims from text and surface related evidence, rather than treating a model verdict as proof.

> **Snapshot status:** This repository contains the original public backend prototype. It does not provide a runnable end-to-end app.

## What you can inspect

| Part | What is in this snapshot |
| --- | --- |
| Verification and retrieval | [`Backend/Advisor/Analyser.py`](Backend/Advisor/Analyser.py) includes claim extraction, model-assisted verification with source links, embedding similarity, and linguistic scoring. Its code references Chroma DB for local storage. |
| Ingestion | [`Backend/Advisor/ScraperModels.py`](Backend/Advisor/ScraperModels.py) contains source-extraction helpers. The team also explored screenshot ingestion and OCR. |
| Backend interface | [`Backend/manage.py`](Backend/manage.py) and [`Backend/Advisor/views.py`](Backend/Advisor/views.py) show the Django project entry point and prototype API views. |
| Frontend | [`.gitmodules`](.gitmodules) points to a separate React repository that is not publicly accessible. The frontend cannot be checked out from this repository alone. |

## What you can run

Clone normally **without initializing submodules** to inspect the backend source. With Python 3, you can run a syntax-only check from the repository root. This does not import dependencies, make network calls, or exercise the API:

```sh
python3 -m py_compile Backend/manage.py Backend/Advisor/Analyser.py Backend/Advisor/ScraperModels.py Backend/Advisor/views.py
```

The live backend is not a turnkey demo. It uses external model services and requires valid service credentials and project-specific configuration. Neither a working deployment nor end-to-end setup is documented here.

The code is a hackathon prototype, not a validated fact-checking service. Similarity to other sources and linguistic heuristics can help find leads, but neither establishes that a claim is true. The snapshot does not include a reproducible benchmark.

## Credits

Built by the Truthflow hackathon team. Praneeth Suresh worked on the backend claim and source analysis.
