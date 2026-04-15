# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import Sourcefile
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
