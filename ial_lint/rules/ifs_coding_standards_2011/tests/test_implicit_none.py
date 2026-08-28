# SPDX-FileCopyrightText: 2026 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileComment: In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import Sourcefile
from loki.lint import DefaultHandler

from conftest import run_linter

from ial_lint.rules import ifs_coding_standards_2011 as rules


def test_implicit_none():
    fcode = """
subroutine routine_okay
implicit none
integer :: a
a = 5
contains
subroutine contained_routine_okay
integer :: b
b = 5
end subroutine contained_routine_okay
end subroutine routine_okay

module mod_okay
implicit none
contains
subroutine contained_mod_routine_okay
integer :: a
a = 5
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
    _ = run_linter(source, [rules.ImplicitNoneRule], handlers=[handler])

    assert len(messages) == 5
    assert all('"IMPLICIT NONE"' in msg for msg in messages)
    assert all('[4.4]' in msg for msg in messages)
    assert sum('"routine_not_okay"' in msg for msg in messages) == 1
    assert sum('"routine_also_not_okay"' in msg for msg in messages) == 1
    assert sum('"contained_routine_not_okay"' in msg for msg in messages) == 1
    assert sum('"contained_mod_routine_not_okay"' in msg for msg in messages) == 1
    assert sum('"contained_contained_routine_not_okay"' in msg for msg in messages) == 1
