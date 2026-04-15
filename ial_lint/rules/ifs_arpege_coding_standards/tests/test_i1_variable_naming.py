# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import Sourcefile
from loki.lint import DefaultHandler

from conftest import run_linter

from ial_lint.rules import ifs_arpege_coding_standards as rules


def test_i1_variable_naming():
    fcode = """
module i1_var_mod
  implicit none
  type :: some_t
    integer :: i
  end type some_t
contains
  subroutine i1_var_test(karg, parg, ldflag, yddt, iarg, zarg, llflag, yllocal_arg)
    implicit none
    integer, intent(in) :: karg, iarg
    real, intent(inout) :: parg, zarg
    logical, intent(in) :: ldflag, llflag
    type(some_t), intent(inout) :: yddt, yllocal_arg
    integer :: ilocal, klocal
    real :: zlocal, plocal
    logical :: lllocal, ldlocal
    type(some_t) :: yllocal, yddt_local
  end subroutine i1_var_test
end module i1_var_mod
    """.strip()
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.VariableNamingRule], handlers=[handler])

    expected_messages = (
        ('[I1]', 'VariableNamingRule', 'Dummy argument "iarg" should start with "K"', '(l. 9)'),
        ('[I1]', 'VariableNamingRule', 'Dummy argument "zarg" should start with "P"', '(l. 10)'),
        ('[I1]', 'VariableNamingRule', 'Dummy argument "llflag" should start with "LD"', '(l. 11)'),
        ('[I1]', 'VariableNamingRule', 'Dummy argument "yllocal_arg" should start with "YD"', '(l. 12)'),
        ('[I1]', 'VariableNamingRule', 'Local variable "klocal" should start with "I"', '(l. 13)'),
        ('[I1]', 'VariableNamingRule', 'Local variable "plocal" should start with "Z"', '(l. 14)'),
        ('[I1]', 'VariableNamingRule', 'Local variable "ldlocal" should start with "LL"', '(l. 15)'),
        ('[I1]', 'VariableNamingRule', 'Local variable "yddt_local" should start with "YL"', '(l. 16)'),
    )

    assert len(messages) == len(expected_messages)
    for keywords in expected_messages:
        assert any(all(keyword in msg for keyword in keywords) for msg in messages)
