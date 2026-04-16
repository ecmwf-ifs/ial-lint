# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os
from pathlib import Path

from loki import Sourcefile
from loki.lint import DefaultHandler

from conftest import run_linter

from ial_lint.rules import ifs_arpege_coding_standards as rules


def _run_i1_with_fix(fcode):
    source = Sourcefile.from_source(fcode)
    source.path = Path(__file__).parent / 'i1_variable_naming_fix_test.F90'
    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.VariableNamingRule], config={'fix': True}, handlers=[handler])
    return source, messages


def _cleanup_fixed_source(source):
    if source.path and Path(source.path).exists():
        os.remove(source.path)


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


def test_i1_fix_variable_naming_local_variables_only():
    fcode = """
subroutine i1_fix_var_test(karg)
  implicit none
  integer, intent(in) :: karg
  integer :: klocal
  real :: plocal
  logical :: ldlocal

  klocal = karg
  plocal = 1.0
  ldlocal = .true.
end subroutine i1_fix_var_test
    """.strip()
    source, messages = _run_i1_with_fix(fcode)

    expected_messages = (
        ('[I1]', 'VariableNamingRule', 'Local variable "klocal" should start with "I"'),
        ('[I1]', 'VariableNamingRule', 'Local variable "plocal" should start with "Z"'),
        ('[I1]', 'VariableNamingRule', 'Local variable "ldlocal" should start with "LL"'),
    )

    assert len(messages) == len(expected_messages)
    for keywords in expected_messages:
        assert any(all(keyword in msg for keyword in keywords) for msg in messages)

    rendered = source.to_fortran()
    assert 'INTEGER :: Ilocal' in rendered
    assert 'REAL :: Zlocal' in rendered
    assert 'LOGICAL :: LLlocal' in rendered
    assert 'Ilocal = karg' in rendered
    assert 'Zlocal = 1.0' in rendered
    assert 'LLlocal = .true.' in rendered
    assert 'INTEGER :: klocal' not in rendered
    assert 'REAL :: plocal' not in rendered
    assert 'LOGICAL :: ldlocal' not in rendered
    _cleanup_fixed_source(source)


def test_i1_fix_variable_naming_skips_collisions():
    fcode = """
subroutine i1_fix_var_collision_test
  implicit none
  integer :: ilocal, klocal

  klocal = 1
  ilocal = klocal
end subroutine i1_fix_var_collision_test
    """.strip()
    source, messages = _run_i1_with_fix(fcode)

    assert len(messages) == 1
    assert 'Local variable "klocal" should start with "I"' in messages[0]

    rendered = source.to_fortran().lower()
    assert 'integer :: ilocal, klocal' in rendered
    assert 'ilocal = klocal' in rendered
    _cleanup_fixed_source(source)


def test_i1_fix_variable_naming_does_not_rename_dummy_arguments():
    fcode = """
subroutine i1_fix_dummy_test(iarg)
  implicit none
  integer, intent(in) :: iarg
  integer :: klocal

  klocal = iarg
end subroutine i1_fix_dummy_test
    """.strip()
    source, messages = _run_i1_with_fix(fcode)

    assert len(messages) == 2
    assert any('Dummy argument "iarg" should start with "K"' in msg for msg in messages)
    assert any('Local variable "klocal" should start with "I"' in msg for msg in messages)

    rendered = source.to_fortran()
    assert 'SUBROUTINE i1_fix_dummy_test (iarg)' in rendered
    assert 'INTEGER, INTENT(IN) :: iarg' in rendered
    assert 'INTEGER :: Ilocal' in rendered
    assert 'Ilocal = iarg' in rendered
    _cleanup_fixed_source(source)
