# CI gate evidence

Proof that the pipeline in `.github/workflows/ci.yml` passes on a clean clone and **fails the build
when a test is broken**, as Task 3.3 of Module 3 asks. A test was broken on purpose, pushed, the failed
run captured, and the break reverted. Every run below is on the `Week-3` branch of
`jimmyls92/10x-engineer-project-repo`, triggered by a push. Facts are taken from `gh run view`.

| # | Run | Commit | Started (UTC) | Result |
|---|---|---|---|---|
| 1 | [37490611819](https://github.com/jimmyls92/10x-engineer-project-repo/actions/runs/37490611819) | `b77e6ea` Add CI workflow with lint and coverage gate | 2026-10-06 15:48:34 | ✓ success |
| 2 | [37491674238](https://github.com/jimmyls92/10x-engineer-project-repo/actions/runs/37491674238) | `8632b84` Break health test to prove the CI gate | 2026-10-06 15:56:20 | ✗ failure |
| 3 | [37492120010](https://github.com/jimmyls92/10x-engineer-project-repo/actions/runs/37492120010) | `81d514d` Revert "Break health test to prove the CI gate" | 2026-10-06 15:59:38 | ✓ success |

## What the gate checks

One job, `test`, on `ubuntu-latest`, with every `run` step in `backend/`:

| Brief requirement | How `ci.yml` meets it |
|---|---|
| Triggers on push and pull request | `on: [push, pull_request]`, on any branch |
| Sets up the Python environment and installs dependencies | `actions/setup-python@v7` with `python-version: '3.12'` (the pinned FastAPI 0.109.0 and Pydantic 2.5.3 need 3.10-3.12), then `pip install -r requirements.txt` |
| Runs linting (ruff or flake8) | `ruff check .`, ruff pinned to `0.16.10` in `requirements.txt`, rules in the committed `backend/ruff.toml` (`E4`, `E7`, `E9`, `F`) |
| Runs tests with coverage | `pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80` |
| Fails the build if coverage drops below 80% | `--cov-fail-under=80` makes pytest exit non-zero below 80%, which fails the step |
| Passes on a clean clone | Run 1, below |

Lint runs before the tests, and a failed step stops the job, so a lint error fails the build without
running the tests.

## Passes on a clean clone

Each Actions run starts from a fresh checkout of the pushed commit (`actions/checkout@v7`) on a new
runner, and installs only what the repository declares. Run 1 is the first run of the workflow:

- **Install dependencies** installed exactly the pins, among them `fastapi-0.109.0`,
  `pydantic-2.5.3`, `pytest-7.4.4`, `pytest-cov-4.1.0` and `ruff-0.16.10`.
- **Lint**: `All checks passed!`
- **Test with coverage**, on Python 3.12.15 (Linux):
  `Required test coverage of 80% reached. Total coverage: 100.00%` and `360 passed, 506 warnings`.

Everything the run needs is committed: the ruff config (`129762f`) and the ruff pin (`7f8f79e`) went
in before the workflow (`b77e6ea`). Without the config, a clean clone would have linted with ruff's
wider default rules and failed on 80 findings.

## Fails when it should

`8632b84` changed one line of `backend/tests/test_api.py` so the health check expects the wrong
status:

```diff
     def test_health_check(self, client: TestClient):
         response = client.get("/health")
-        assert response.status_code == 200
+        assert response.status_code == 201
```

Run 2 on that commit **failed**. Steps: Set up job ✓, checkout ✓, Set up Python ✓, Install
dependencies ✓, Lint ✓, **Test with coverage ✗**. From its log:

```
tests/test_api.py::TestHealth::test_health_check FAILED                  [  0%]
>       assert response.status_code == 201
E       assert 200 == 201
Required test coverage of 80% reached. Total coverage: 100.00%
FAILED tests/test_api.py::TestHealth::test_health_check - assert 200 == 201
================= 1 failed, 359 passed, 506 warnings in 1.77s ==================
##[error]Process completed with exit code 1.
```

Coverage was still 100%, so the build failed because of the broken test alone: a failing test is
enough to fail the build.

## Back to green

`81d514d` restores `assert response.status_code == 200` and nothing else. It was not made with a
plain `git revert 8632b84`, because that commit also added entries to `docs/prompt-log.md`, and a
whole-commit revert would have deleted them; only the test file was restored from `8632b84^`. Both
the break and its undo stay in the history.

Run 3 on that commit **succeeded**: `All checks passed!`, `Required test coverage of 80% reached.
Total coverage: 100.00%`, `360 passed, 506 warnings`.

## Notes

- **Branch, not `main`.** The brief's verification says `git push origin main`. Each module of this
  course is delivered on its own branch (`Week-3` for Module 3), and `main` is left as it is, so the
  runs above are on `Week-3`. The workflow triggers on every branch, so this changes nothing about
  the gate.
- **Pull request trigger.** `pull_request` is declared in `ci.yml`, but all three runs come from
  pushes; no pull request has been opened.
- **The coverage threshold has not been seen failing.** Coverage is 100%, and the broken test in
  run 2 did not lower it. The 80% gate is shown by the `--cov-fail-under=80` flag and the
  `Required test coverage of 80% reached` line in every run.
- **Runner image.** GitHub annotated run 1: the `ubuntu-latest` label moves to Ubuntu 26 from
  2026-10-19. The workflow does not pin an Ubuntu version.
