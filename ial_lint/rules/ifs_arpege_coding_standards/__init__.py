# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

"""
Implementation of rules from the IFS Arpege coding standards as :any:`GenericRule`

See https://sites.ecmwf.int/docs/ifs-arpege-coding-standards/fortran for the
current version of the coding standards.
"""

from ial_lint.rules.ifs_arpege_coding_standards.l1_implicit_none import *  # noqa
from ial_lint.rules.ifs_arpege_coding_standards.l3_global_variables import *  # noqa
from ial_lint.rules.ifs_arpege_coding_standards.l9_interfaces_for_routines import *  # noqa
