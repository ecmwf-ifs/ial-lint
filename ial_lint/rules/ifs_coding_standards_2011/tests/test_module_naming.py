# SPDX-FileCopyrightText: 2026 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileComment: In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from pathlib import Path

from loki import Sourcefile
from loki.lint import DefaultHandler

from conftest import run_linter

from ial_lint.rules import ifs_coding_standards_2011 as rules


def test_module_naming():
    '''Test file and modules for checking that naming is correct and matches each other.'''
    fcode = """
! This is ok
module module_naming_mod
integer foo
contains
subroutine bar
integer foobar
end subroutine bar
end module module_naming_mod

! This should complain about wrong file name
module MODULE_NAMING_UPPERCASE_MOD
integer foo
contains
subroutine bar
integer foobar
end subroutine bar
end module MODULE_NAMING_UPPERCASE_MOD

! This should complain about wrong module and file name
module module_naming
integer baz
end module module_naming
    """.strip()
    source = Sourcefile.from_source(fcode)
    # We don't actually write the file but simply set the filename to something sensible
    for m in source.modules:
        m.source.file = str(Path(__file__).parent / 'module_naming_mod.f90')
    messages = []
    handler = DefaultHandler(target=messages.append)
    _ = run_linter(source, [rules.ModuleNamingRule], handlers=[handler])

    assert len(messages) == 3
    keywords = ('ModuleNamingRule', '[1.5]')
    assert all(all(keyword in msg for keyword in keywords) for msg in messages)

    assert all('"module_naming' in msg.lower() for msg in messages)
    assert all(keyword in messages[0] for keyword in ('module_naming_mod.f90', 'filename'))
    assert all(keyword in messages[1] for keyword in ('"_mod"', 'Name of module'))
    assert all(keyword in messages[2] for keyword in ('module_naming_mod.f90', 'filename'))
