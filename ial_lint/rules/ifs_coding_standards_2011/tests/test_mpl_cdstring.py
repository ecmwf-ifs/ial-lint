# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import importlib
import pytest

from loki import Sourcefile
from loki.lint import DefaultHandler

from conftest import run_linter


@pytest.fixture(scope='module', name='rules')
def fixture_rules():
    rules = importlib.import_module('ial_lint.rules.ifs_coding_standards_2011')
    return rules


def test_mpl_cdstring(rules):
    fcode = """
subroutine routine_okay
use mpl_module
call mpl_init(cdstring='routine_okay')
end subroutine routine_okay

subroutine routine_also_okay
use MPL_MODULE
call MPL_INIT(KPROCS=5, CDSTRING='routine_also_okay')
end subroutine routine_also_okay

subroutine routine_not_okay
use mpl_module
call mpl_init
end subroutine routine_not_okay

subroutine routine_also_not_okay
use MPL_INIT
call MPL_INIT(kprocs=5)
end subroutine routine_also_not_okay
    """.strip()
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    _ = run_linter(source, [rules.MplCdstringRule], handlers=[handler])
    assert len(messages) == 2
    assert all('[3.12]' in msg for msg in messages)
    assert all('MplCdstringRule' in msg for msg in messages)
    assert all('"CDSTRING"' in msg for msg in messages)
    assert all('MPL_INIT' in msg.upper() for msg in messages)
    assert sum('(l. 13)' in msg for msg in messages) == 1
    assert sum('(l. 18)' in msg for msg in messages) == 1
