# IAL-lint: A Fortran linting package for IFS-Arpege-LAM codes

[![license](https://img.shields.io/github/license/ecmwf-ifs/ial-lint)](https://www.apache.org/licenses/LICENSE-2.0.html)
[![Static Badge](https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity/emerging_badge.svg)](https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity#emerging)
[![pylint](https://github.com/ecmwf-ifs/ial-lint/actions/workflows/pylint.yml/badge.svg)](https://github.com/ecmwf-ifs/ial-lint/actions/workflows/pylint.yml)
[![pytest](https://github.com/ecmwf-ifs/ial-lint/actions/workflows/pytest.yml/badge.svg)](https://github.com/ecmwf-ifs/ial-lint/actions/workflows/pytest.yml)
[![codecov](https://codecov.io/gh/ecmwf-ifs/ial-lint/branch/main/graph/badge.svg?token=9ZDS95SFWI)](https://codecov.io/gh/ecmwf-ifs/ial-lint)

> [!IMPORTANT]
> This software is **Emerging** and subject to ECMWF's guidelines on
> [Software Maturity](https://github.com/ecmwf/codex/raw/refs/heads/main/Project%20Maturity).

**IAL-lint** is a code linting package for IFS-Arpege-LAM (IAL) codes
and components. It aims to provide code validation checks and possible
auto-fixes for these Fortran codes based on the 
[Loki](https://github.com/ecmwf-ifs/loki) package. The
specific rules for these code components are documented in the
[IFS-Arpege-LAM coding
standard](https://github.com/ecmwf-ifs/ifs-arpege-coding-standards)

## Installation

IAL-lint is currently a rule package for Loki's `loki-lint.py` command rather
than a standalone command-line tool. A dedicated IAL-lint CLI may be added in the
future.

For CI pipelines and reproducible jobs, install from a public release or tag:

```bash
python -m pip install \
  "ial-lint @ git+https://github.com/ecmwf-ifs/ial-lint@<version>"
```

The package depends on a pinned Loki release, as declared in
[`pyproject.toml`](pyproject.toml). See the Loki
[installation notes](https://github.com/ecmwf-ifs/loki/blob/main/INSTALL.md) if
your environment also needs optional Loki frontend dependencies.

For local development, create and activate a virtual environment, then install
IAL-lint in editable mode with its test dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[tests]"
```

## Usage

After installation, invoke the rules through Loki's lint command. The default
rules module is `ifs_arpege_coding_standards`:

```bash
loki-lint.py rules
loki-lint.py check --include "path/to/source/**/*.F90"
```

To select a specific IAL-lint rules module explicitly, use `--rules-module`:

```bash
loki-lint.py --rules-module ifs_arpege_coding_standards check --include "path/to/source/**/*.F90"
loki-lint.py --rules-module ifs_coding_standards_2011 check --include "path/to/source/**/*.F90"
```

You can also generate a default configuration file for a rules module:

```bash
loki-lint.py --rules-module ifs_arpege_coding_standards default-config > loki-lint.yml
loki-lint.py --rules-module ifs_arpege_coding_standards check --config loki-lint.yml
```

## Contact

Michael Lange (michael.lange@ecmwf.int),
Balthasar Reuter (balthasar.reuter@ecmwf.int)

## License

IAL-lint is distributed under the [Apache License 2.0](LICENSE). In applying this
licence, ECMWF does not waive the privileges and immunities granted to it by
virtue of its status as an intergovernmental organisation nor does it submit to
any jurisdiction.

## Contributing

Contributions to IAL-lint are welcome. Please read
[CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request.
All participation in this project is governed by the
[Code of Conduct](CODE_OF_CONDUCT.md).
