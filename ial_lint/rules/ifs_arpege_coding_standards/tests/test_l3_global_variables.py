# SPDX-FileCopyrightText: 2026 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileComment: In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import Sourcefile
from loki.lint import DefaultHandler

from conftest import run_linter

from ial_lint.rules import ifs_arpege_coding_standards as rules


def test_only_param_global_var_rule():
    fcode = """
module some_mod
use other_mod, only: some_type
implicit none

integer, parameter :: param_ok = 123
integer, parameter :: arr_param_ok(:) = (/ 1, 2, 3 /)
integer :: var_not_ok
integer, allocatable :: arr_not_ok(:), other_arr_not_ok(:,:)
integer, pointer :: ptr_not_ok
real, parameter :: rparam_ok = -42.
type(some_type) :: dt_var_not_ok
type(some_type) :: dt_arr_not_ok(2)
end module some_mod
    """
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.OnlyParameterGlobalVarRule], handlers=[handler])

    expected_messages = (
        (['L3', 'OnlyParameterGlobalVarRule', 'var_not_ok', '(l. 8)']),
        (['L3', 'OnlyParameterGlobalVarRule', 'arr_not_ok', 'other_arr_not_ok', '(l. 9)']),
        (['L3', 'OnlyParameterGlobalVarRule', 'ptr_not_ok', '(l. 10)']),
        (['L3', 'OnlyParameterGlobalVarRule', 'dt_var_not_ok', '(l. 12)']),
        (['L3', 'OnlyParameterGlobalVarRule', 'dt_arr_not_ok', '(l. 13)']),
    )

    assert len(messages) == len(expected_messages)
    for msg, keywords in zip(messages, expected_messages):
        for keyword in keywords:
            assert keyword in msg
