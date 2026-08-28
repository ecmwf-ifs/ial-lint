# SPDX-FileCopyrightText: 2026 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileComment: In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from importlib.metadata import version, PackageNotFoundError

from ial_lint.rules import *  # noqa

try:
    __version__ = version("ial_lint")
except PackageNotFoundError:
    # package is not installed
    pass
