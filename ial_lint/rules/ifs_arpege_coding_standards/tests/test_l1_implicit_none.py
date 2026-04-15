# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os
from pathlib import Path

from loki import FindNodes, Sourcefile
from loki import ir
from loki.lint import DefaultHandler

from conftest import run_linter

from ial_lint.rules import ifs_arpege_coding_standards as rules


def _get_messages(fcode):
    """Run the L1 rule on the given source and collect messages."""
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.MissingImplicitNoneRule], handlers=[handler])
    return messages


def _run_l1_with_fix(fcode):
    """Run the L1 rule with fixing enabled and collect messages."""
    source = Sourcefile.from_source(fcode)
    source.path = Path(__file__).parent / 'l1_implicit_none_fix_test.F90'
    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.MissingImplicitNoneRule], config={'fix': True}, handlers=[handler])
    return source, messages


def _cleanup_fixed_source(source):
    if source.path and Path(source.path).exists():
        os.remove(source.path)


def _get_implicit_none_count(ir_):
    return sum(intr.text == 'NONE' for intr in FindNodes(ir.ImplicitStmt).visit(ir_))


def _apply_l1_module_fix(fcode):
    """Apply the L1 module fixer directly and return the mutated module."""
    source = Sourcefile.from_source(fcode)
    module = source.modules[0]
    report = type('RuleReport', (), {'problem_reports': (), 'rule': rules.MissingImplicitNoneRule})()
    rules.MissingImplicitNoneRule.fix_module(module, report, {})
    return source, module


def _assert_messages(messages, expected_messages):
    assert len(messages) == len(expected_messages)
    unmatched_messages = list(messages)
    for keywords in expected_messages:
        for idx, msg in enumerate(unmatched_messages):
            if all(keyword in msg for keyword in keywords):
                del unmatched_messages[idx]
                break
        else:
            raise AssertionError(f'No message matched keywords: {keywords}')


def test_l1_missing_implicit_none():
    fcode = """
subroutine routine_okay
implicit none
integer :: a
a = 5
contains
subroutine contained_routine_not_okay
! This should report
integer :: b
b = 5
end subroutine contained_routine_not_okay
end subroutine routine_okay

module mod_okay
implicit none
contains
subroutine contained_mod_routine_okay
integer :: a
a = 5
contains
subroutine contained_mod_routine_contained_routine_okay
integer :: b
b = 2
end subroutine contained_mod_routine_contained_routine_okay
end subroutine contained_mod_routine_okay
end module mod_okay

subroutine routine_not_okay
! This should report
integer :: a
a = 5
contains
subroutine contained_not_okay_routine_okay
implicit none
integer :: b
b = 5
end subroutine contained_not_okay_routine_okay
end subroutine routine_not_okay

module mod_not_okay
contains
subroutine contained_mod_not_okay_routine_okay
implicit none
integer :: a
a = 5
end subroutine contained_mod_not_okay_routine_okay
end module mod_not_okay

subroutine routine_also_not_okay
! This should report
integer :: a
a = 5
contains
subroutine contained_routine_not_okay
! This should report
integer :: b
b = 5
end subroutine contained_routine_not_okay
end subroutine routine_also_not_okay

module mod_also_not_okay
contains
subroutine contained_mod_routine_not_okay
! This should report
integer :: a
a = 5
contains
subroutine contained_contained_routine_not_okay
! This should report
integer :: b
b = 5
end subroutine contained_contained_routine_not_okay
end subroutine contained_mod_routine_not_okay
end module mod_also_not_okay
    """
    messages = _get_messages(fcode)

    expected_messages = (
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'mod_not_okay', '(l. 40)']),
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'mod_also_not_okay', '(l. 61)']),
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'contained_mod_routine_not_okay', '(l. 63)']),
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'contained_contained_routine_not_okay', '(l. 68)']),
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'routine_not_okay', '(l. 28)']),
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'routine_also_not_okay', '(l. 49)']),
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'contained_routine_not_okay', '(l. 54)']),
    )

    _assert_messages(messages, expected_messages)


def test_l1_redundant_implicit_none():
    fcode = """
module mod_with_redundant_implicit_none
implicit none
contains
subroutine contained_routine_redundant
implicit none
integer :: a
a = 5
contains
subroutine nested_routine_redundant
implicit none
integer :: b
b = 2
end subroutine nested_routine_redundant
end subroutine contained_routine_redundant
end module mod_with_redundant_implicit_none

subroutine standalone_routine_okay
implicit none
integer :: c
c = 1
end subroutine standalone_routine_okay
    """
    messages = _get_messages(fcode)

    expected_messages = (
        (['[L1]', 'MissingImplicitNoneRule', 'Redundant `IMPLICIT NONE` found',
          'contained_routine_redundant', '(l. 5)']),
        (['[L1]', 'MissingImplicitNoneRule', 'Redundant `IMPLICIT NONE` found',
          'nested_routine_redundant', '(l. 10)']),
    )

    _assert_messages(messages, expected_messages)


def test_l1_non_none_implicit_does_not_satisfy_rule():
    assert not rules.MissingImplicitNoneRule.check_for_implicit_none(
        ir.Section(body=(ir.ImplicitStmt(text='INTEGER(A-Z)'),))
    )
    assert not rules.MissingImplicitNoneRule.check_for_implicit_none(
        ir.Section(body=(ir.ImplicitStmt(text='REAL(A-H,O-Z)'),))
    )
    assert rules.MissingImplicitNoneRule.check_for_implicit_none(
        ir.Section(body=(ir.ImplicitStmt(text='NONE'),))
    )


def test_l1_fix_module_adds_missing_implicit_none():
    fcode = """
module mod_missing_implicit_none
use some_mod, only: some_type
integer :: a
type(some_type) :: b
end module mod_missing_implicit_none
    """
    source, module = _apply_l1_module_fix(fcode)

    assert _get_implicit_none_count(module.spec) == 1

    rendered = source.to_fortran().lower()
    use_idx = rendered.index('use some_mod, only: some_type')
    implicit_idx = rendered.index('implicit none')
    integer_idx = rendered.index('integer :: a')
    assert use_idx < implicit_idx < integer_idx


def test_l1_fix_module_removes_redundant_implicit_none_in_contained_routines():
    fcode = """
module mod_with_redundant_implicit_none
implicit none
contains
subroutine contained_routine_redundant
implicit none
integer :: a
a = 5
contains
subroutine nested_routine_redundant
implicit none
integer :: b
b = 2
end subroutine nested_routine_redundant
end subroutine contained_routine_redundant
end module mod_with_redundant_implicit_none
    """
    source, module = _apply_l1_module_fix(fcode)

    contained = module['contained_routine_redundant']
    nested = contained['nested_routine_redundant']

    assert _get_implicit_none_count(module.spec) == 1
    assert _get_implicit_none_count(contained.spec) == 0
    assert _get_implicit_none_count(nested.spec) == 0

    rendered = source.to_fortran().lower()
    assert rendered.count('implicit none') == 1


def test_l1_fix_subroutine_adds_missing_implicit_none_when_no_parent_has_it():
    fcode = """
subroutine routine_missing_implicit_none
use some_mod, only: some_type
integer :: a
type(some_type) :: b
a = 5
end subroutine routine_missing_implicit_none
    """
    source, messages = _run_l1_with_fix(fcode)

    _assert_messages(messages, (
        ['[L1]', 'MissingImplicitNoneRule', 'routine_missing_implicit_none', 'No `IMPLICIT NONE` found'],
    ))

    routine = source['routine_missing_implicit_none']
    assert _get_implicit_none_count(routine.spec) == 1

    rendered = source.to_fortran().lower()
    use_idx = rendered.index('use some_mod, only: some_type')
    implicit_idx = rendered.index('implicit none')
    integer_idx = rendered.index('integer :: a')
    assert use_idx < implicit_idx < integer_idx
    _cleanup_fixed_source(source)


def test_l1_fix_does_not_add_routine_implicit_none_when_module_already_has_it():
    fcode = """
module mod_with_inherited_implicit_none
implicit none
contains
subroutine routine_inheriting_implicit_none
integer :: a
a = 5
end subroutine routine_inheriting_implicit_none
end module mod_with_inherited_implicit_none
    """
    source, messages = _run_l1_with_fix(fcode)

    assert not messages

    module = source['mod_with_inherited_implicit_none']
    routine = module['routine_inheriting_implicit_none']
    assert _get_implicit_none_count(module.spec) == 1
    assert _get_implicit_none_count(routine.spec) == 0

    rendered = source.to_fortran().lower()
    assert rendered.count('implicit none') == 1
    _cleanup_fixed_source(source)
