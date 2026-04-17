# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os
from pathlib import Path

from loki import Sourcefile, SubstituteExpressions
from loki.lint import DefaultHandler

from conftest import run_linter

from ial_lint.rules import ifs_arpege_coding_standards as rules


def _run_i2_with_fix(fcode):
    source = Sourcefile.from_source(fcode)
    source.path = Path(__file__).parent / 'i2_kind_specification_fix_test.F90'
    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.KindSpecificationRule], config={'fix': True}, handlers=[handler])
    return source, messages


def _cleanup_fixed_source(source):
    if source.path and Path(source.path).exists():
        os.remove(source.path)


def _read_fixed_source(source):
    return Path(source.path).read_text() if source.path and Path(source.path).exists() else source.to_fortran()


def _apply_i2_module_fix(fcode):
    source = Sourcefile.from_source(fcode)
    module = source.modules[0]
    report = type('RuleReport', (), {'problem_reports': (), 'rule': rules.KindSpecificationRule})()
    rules.KindSpecificationRule.fix_module(module, report, rules.KindSpecificationRule.config)
    return source, module


def _apply_i2_subroutine_fix(fcode):
    source = Sourcefile.from_source(fcode)
    subroutine = source.subroutines[0]
    mapper = rules.KindSpecificationRule.fix_subroutine(
        subroutine, None, rules.KindSpecificationRule.config
    )
    if mapper:
        subroutine.spec = SubstituteExpressions(mapper).visit(subroutine.spec)
    return source, subroutine


def test_i2_kind_specification_declarations():
    fcode = """
module i2_kind_mod
  use parkind1, only: jpim, jprb
  implicit none
  integer(kind=jpim) :: i_ok
  real(kind=jprb) :: r_ok
  integer :: i_missing
  real :: r_missing
  integer(kind=1) :: i_bad
  real(kind=8) :: r_bad
contains
  subroutine i2_kind_sub(k_ok, p_ok)
    use parkind1, only: jpim, jprb
    implicit none
    integer(kind=jpim), intent(in) :: k_ok
    real(kind=jprb), intent(inout) :: p_ok
    integer :: k_missing
    real :: p_missing
    integer(kind=1) :: k_bad
    real(kind=8) :: p_bad
  end subroutine i2_kind_sub
end module i2_kind_mod
    """.strip()
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.KindSpecificationRule], handlers=[handler])

    expected_messages = (
        ('[I2]', 'KindSpecificationRule', 'i_missing declared without explicit KIND', '(l. 6)'),
        ('[I2]', 'KindSpecificationRule', 'r_missing declared without explicit KIND', '(l. 7)'),
        ('[I2]', 'KindSpecificationRule', '1 is not an allowed KIND value for i_bad', '(l. 8)'),
        ('[I2]', 'KindSpecificationRule', '8 is not an allowed KIND value for r_bad', '(l. 9)'),
        ('[I2]', 'KindSpecificationRule', 'k_missing declared without explicit KIND', '(l. 16)'),
        ('[I2]', 'KindSpecificationRule', 'p_missing declared without explicit KIND', '(l. 17)'),
        ('[I2]', 'KindSpecificationRule', '1 is not an allowed KIND value for k_bad', '(l. 18)'),
        ('[I2]', 'KindSpecificationRule', '8 is not an allowed KIND value for p_bad', '(l. 19)'),
    )

    assert len(messages) == len(expected_messages)
    for keywords in expected_messages:
        assert any(all(keyword in msg for keyword in keywords) for msg in messages)


def test_i2_fix_kind_specification_module_scope():
    fcode = """
module i2_fix_kind_mod
  use parkind1, only: jpim, jprb
  implicit none
  integer :: i_missing
  real(kind=8) :: r_bad
contains
  subroutine i2_fix_kind_sub
    implicit none
    integer :: k_missing
    real(kind=8) :: p_bad
  end subroutine i2_fix_kind_sub
end module i2_fix_kind_mod
    """.strip()

    source, _ = _apply_i2_module_fix(fcode)
    rendered = source.to_fortran().lower()
    assert 'integer(kind=jpim) :: i_missing' in rendered
    assert 'real(kind=jprb) :: r_bad' in rendered

def test_i2_fix_kind_specification_subroutine_scope():
    sub_fcode = """
subroutine i2_fix_kind_sub
  use parkind1, only: jpim, jprb
  implicit none
  integer :: k_missing
  real(kind=8) :: p_bad
end subroutine i2_fix_kind_sub
    """.strip()
    source, _ = _apply_i2_subroutine_fix(sub_fcode)

    rendered = source.to_fortran().lower()
    assert 'integer(kind=jpim) :: k_missing' in rendered
    assert 'real(kind=jprb) :: p_bad' in rendered


def test_i2_fix_kind_specification_skips_without_visible_kind_symbols():
    fcode = """
subroutine i2_fix_kind_no_imports
  implicit none
  integer :: i_missing
  real(kind=8) :: r_bad
end subroutine i2_fix_kind_no_imports
    """.strip()
    source, messages = _run_i2_with_fix(fcode)

    assert len(messages) == 2
    rendered = _read_fixed_source(source).lower()
    assert 'integer :: i_missing' in rendered
    assert 'real(kind=8) :: r_bad' in rendered
    _cleanup_fixed_source(source)
