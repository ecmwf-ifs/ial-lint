# SPDX-FileCopyrightText: 2026 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileComment: In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import Sourcefile
from loki.lint import DefaultHandler

from conftest import run_linter

from ial_lint.rules import ifs_coding_standards_2011 as rules


def test_dr_hook_okay():
    fcode = """
subroutine routine_okay
use yomhook, only: lhook, dr_hook
real(kind=jprb) :: zhook_handle

! Comments are non-executable statements

if (lhook) then
#define foobar
  call dr_hook('routine_okay', 0, zhook_handle)
end if

print *, "Foo bar"

if (lhook) call dr_hook('routine_okay', 1, zhook_handle)

! Comments are non-executable statements

contains

subroutine routine_contained_okay
real(kind=jprb) :: zhook_handle

! CPP directives should be ignored
#ifndef _some_macro

if (lhook) call dr_hook('routine_okay%routine_contained_okay', 0, zhook_handle)

print *, "Foo bar"

if (lhook) call dr_hook('routine_okay%routine_contained_okay', 1, zhook_handle)

! CPP directives should be ignored
#endif
end subroutine routine_contained_okay
end subroutine routine_okay
    """.strip()
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    _ = run_linter(source, [rules.DrHookRule], handlers=[handler])
    assert len(messages) == 0


def test_dr_hook_routine():
    fcode = """
subroutine routine_not_okay_a
use yomhook, only: lhook, dr_hook
real(kind=jprb) :: zhook_handle

! Error: no conditional IF(LHOOK)
! Error: no zhook_handle (Not detected because call not found)
call dr_hook('routine_not_okay_a', 0)

print *, "Foo bar"

! Error: subroutine name not in string argument
if (lhook) call dr_hook('foobar', 1, zhook_handle)
end subroutine routine_not_okay_a


subroutine routine_not_okay_b
use yomhook, only: lhook, dr_hook
real(kind=jprb) :: zhook_handle

! Error: second argument is not 0 or 1
if (lhook) call dr_hook('routine_not_okay_b', 2, zhook_handle)

print *, "Foo bar"

! Error: third argument is not zhook_handle
if (lhook) call dr_hook('routine_not_okay_b', 1)
end subroutine routine_not_okay_b


subroutine routine_not_okay_c
use yomhook, only: lhook, dr_hook
real(kind=jprb) :: zhook_handle
real(kind=jprb) :: red_herring

red_herring = 1.0

! Error: Executable statement before call to dr_hook
if (lhook) call dr_hook('routine_not_okay_c', 2, zhook_handle)

print *, "Foo bar"

! Error: Executable statement after call to dr_hook
if (lhook) then
  call dr_hook('routine_not_okay_c', 1, zhook_handle)
  red_herring = 2.0
end if

end subroutine routine_not_okay_c


subroutine routine_not_okay_d
use yomhook, only: lhook, dr_hook
real(kind=jprb) :: zhook_handle
real(kind=jprb) :: red_herring

! Error: First call to dr_hook is missing

red_herring = 1.0
print *, "Foo bar"

if (lhook) call dr_hook('routine_not_okay_d', 1, zhook_handle)

end subroutine routine_not_okay_d


subroutine routine_not_okay_e
use yomhook, only: lhook, dr_hook
real(kind=jprb) :: zhook_handle
real(kind=jprb) :: red_herring

if (lhook) call dr_hook('routine_not_okay_e', 0, zhook_handle)

red_herring = 1.0
print *, "Foo bar"

! Error: Last call to dr_hook is missing

contains

subroutine routine_contained_not_okay
use yomhook, only: lhook, dr_hook
real(kind=jprb) :: zhook_handle
real(kind=jprb) :: red_herring

if (lhook) call dr_hook('routine_not_okay_e%routine_contained_not_okay', 0, zhook_handle)

red_herring = 1.0
print *, "Foo bar"

! Error: String argument is not "<parent routine>%<contained routine>"
if (lhook) call dr_hook('routine_contained_not_okay', 1, zhook_handle)
end subroutine routine_contained_not_okay
end subroutine routine_not_okay_e
    """.strip()
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    _ = run_linter(source, [rules.DrHookRule], handlers=[handler])

    assert len(messages) == 9
    keywords = ('DrHookRule', 'DR_HOOK', '[1.9]')
    assert all(all(keyword in msg for keyword in keywords) for msg in messages)

    assert all('First executable statement must be call to DR_HOOK' in messages[i] for i in [0, 4, 6])
    assert all('Last executable statement must be call to DR_HOOK' in messages[i] for i in [5, 7])
    assert all('String argument to DR_HOOK call should be "' in messages[i] for i in [1, 8])
    assert 'Second argument to DR_HOOK call should be "0"' in messages[2]
    assert 'Third argument to DR_HOOK call should be "ZHOOK_HANDLE"' in messages[3]

    # Later lines come first as modules are checked before subroutines
    assert '(l. 12)' in messages[1]
    assert '(l. 21)' in messages[2]
    assert '(l. 26)' in messages[3]
    assert '(l. 91)' in messages[8]

    assert all(f'routine_not_okay_{letter}' in messages[i]
               for letter, i in (('a', 0), ('c', 4), ('c', 5), ('d', 6), ('e', 7)))


def test_dr_hook_module():
    fcode = """
module some_mod

contains

subroutine mod_routine_okay
use yomhook, only: lhook, dr_hook
real(kind=jprb) :: zhook_handle

if (lhook) call dr_hook('some_mod:mod_routine_okay', 0, zhook_handle)
print *, "Foo bar"
if (lhook) call dr_hook('some_mod:mod_routine_okay', 1, zhook_handle)

contains

subroutine mod_contained_routine_okay
use yomhook, only: lhook, dr_hook
real(kind=jprb) :: zhook_handle

if (lhook) call dr_hook('some_mod:mod_routine_okay%mod_contained_routine_okay', 0, zhook_handle)
print *, "Foo bar"
if (lhook) call dr_hook('some_mod:mod_routine_okay%mod_contained_routine_okay', 1, zhook_handle)
end subroutine mod_contained_routine_okay
end subroutine mod_routine_okay

subroutine mod_routine_not_okay
use yomhook, only: lhook, dr_hook
real(kind=jprb) :: zhook_handle

! Error: String argument does not contain module name
if (lhook) call dr_hook('mod_routine_okay', 0, zhook_handle)
print *, "Foo bar"
if (lhook) call dr_hook('some_mod:mod_routine_not_okay', 1, zhook_handle)

contains

subroutine mod_contained_routine_not_okay
use yomhook, only: lhook, dr_hook
real(kind=jprb) :: zhook_handle

! Error: String argument does not contain module name
if (lhook) call dr_hook('mod_routine_not_okay%mod_contained_routine_not_okay', 0, zhook_handle)
print *, "Foo bar"
! Error: String argument does not contain parent routine name
! Error: Second argument is not 0 or 1
if (lhook) call dr_hook('some_mod:mod_contained_routine_not_okay', 8, zhook_handle)
end subroutine mod_contained_routine_not_okay
end subroutine mod_routine_not_okay
end module some_mod
    """.strip()
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    _ = run_linter(source, [rules.DrHookRule], handlers=[handler])

    assert len(messages) == 4
    keywords = ('DrHookRule', 'DR_HOOK', '[1.9]')
    assert all(all(keyword in msg for keyword in keywords) for msg in messages)

    assert all('String argument to DR_HOOK call should be "' in messages[i] for i in [0, 1, 2])
    assert 'Second argument to DR_HOOK call should be "1"' in messages[3]

    # Later lines come first as modules are checked before subroutines
    assert '(l. 30)' in messages[0]
    assert '(l. 41)' in messages[1]
    assert '(l. 45)' in messages[2]
    assert '(l. 45)' in messages[3]
