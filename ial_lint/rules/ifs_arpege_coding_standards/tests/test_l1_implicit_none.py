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


def test_implicit_none():
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
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.MissingImplicitNoneRule], handlers=[handler])

    expected_messages = (
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'mod_not_okay', '(l. 40)']),
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'mod_also_not_okay', '(l. 61)']),
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'contained_mod_routine_not_okay', '(l. 63)']),
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'contained_contained_routine_not_okay', '(l. 68)']),
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'contained_routine_not_okay', '(l. 7)']),
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'routine_not_okay', '(l. 28)']),
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'routine_also_not_okay', '(l. 49)']),
        (['[L1]', 'MissingImplicitNoneRule', '`IMPLICIT NONE`', 'contained_routine_not_okay', '(l. 54)']),
    )

    assert len(messages) == len(expected_messages)
    for msg, keywords in zip(messages, expected_messages):
        for keyword in keywords:
            assert keyword in msg
