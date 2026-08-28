<!--
SPDX-FileCopyrightText: 2026 European Centre for Medium-Range Weather Forecasts (ECMWF)
SPDX-License-Identifier: Apache-2.0
SPDX-FileComment: In applying this licence, ECMWF does not waive the privileges and immunities
granted to it by virtue of its status as an intergovernmental organisation
nor does it submit to any jurisdiction.
-->

# Contributing to IAL-lint

Thank you for your interest in contributing to IAL-lint. IAL-lint is an ECMWF
rule package for validating IFS-Arpege-LAM Fortran code through Loki's
`loki-lint.py` command.

## Before You Start

For non-trivial changes, please open or comment on an issue first so the
approach, scope, and expected review effort can be discussed with the
maintainers.

By opening a pull request, you agree that your contribution is made under
IAL-lint's licence, the Apache License Version 2.0, and under the terms of the
ECMWF Contributor Licence Agreement:

<https://github.com/ecmwf/codex/blob/main/Legal/Contributor-License-Agreement.md>

## Development Setup

Create and activate a virtual environment, then install IAL-lint in editable
mode with its test dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[tests]"
```

The package depends on Loki. See the Loki
[installation notes](https://github.com/ecmwf-ifs/loki/blob/main/INSTALL.md) if
your environment needs optional Loki frontend dependencies.

## Making Changes

Keep changes focused and reviewable. Prefer small, direct changes that preserve
the existing rule APIs and coding style unless a broader change has been agreed
with the maintainers.

New or changed lint behaviour should include tests. Keep test inputs minimal and
targeted to the rule behaviour under test.

## Local Validation

Run the test suite:

```bash
python -m pytest --cov=ial_lint --cov-report=xml
```

Run linting for changed Python code:

```bash
pylint --rcfile=.pylintrc ial_lint
```

Check licensing metadata:

```bash
reuse lint
```

## Pull Requests

Submit contributions through a GitHub pull request against `main`.

Before requesting review:

- Make sure the pull request has a clear description of the problem, solution,
  and any trade-offs.
- Link relevant issues or discussions.
- Include tests or explain why tests are not applicable.
- Update documentation when behaviour, public APIs, or user workflows change.
- Self-review the diff and remove accidental debug code or generated artefacts.
- Ensure CI checks pass.

ECMWF maintainers review pull requests for correctness, maintainability,
licensing, and project fit. Public contributions may require maintainer approval
before CI is run.

## Code of Conduct

All participation in this project is governed by the IAL-lint
[Code of Conduct](CODE_OF_CONDUCT.md).
