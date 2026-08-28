# SPDX-FileCopyrightText: 2026 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileComment: In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

"""
Implementation of rules in the IFS coding standards document (2011) for loki-lint.
"""

from ial_lint.rules.ifs_coding_standards_2011.banned_statements import *  # noqa
from ial_lint.rules.ifs_coding_standards_2011.code_body import *  # noqa
from ial_lint.rules.ifs_coding_standards_2011.dr_hook import *  # noqa
from ial_lint.rules.ifs_coding_standards_2011.explicit_kind import *  # noqa
from ial_lint.rules.ifs_coding_standards_2011.fortran90_operators import *  # noqa
from ial_lint.rules.ifs_coding_standards_2011.implicit_none import *  # noqa
from ial_lint.rules.ifs_coding_standards_2011.limit_subroutine_statements import *  # noqa
from ial_lint.rules.ifs_coding_standards_2011.max_dummy_args import *  # noqa
from ial_lint.rules.ifs_coding_standards_2011.module_naming import *  # noqa
from ial_lint.rules.ifs_coding_standards_2011.mpl_cdstring import *  # noqa
