# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import pytest

from loki import Sourcefile
from loki.lint import DefaultHandler

from conftest import run_linter

from ial_lint.rules import ifs_coding_standards_2011 as rules


def test_banned_statements_default():
    '''Test for banned statements with default.'''
    fcode = """
subroutine banned_statements()
integer :: dummy

dummy = 5
call foobar(dummy)
go to 100
print *, dummy
100 continue
end subroutine banned_statements
    """
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    _ = run_linter(source, [rules.BannedStatementsRule], handlers=[handler])

    assert len(messages) == 3
    keywords = ('BannedStatementsRule', '[4.11]')
    assert all(all(keyword in msg for keyword in keywords) for msg in messages)
    banned_statements = ('GO TO', 'PRINT', 'CONTINUE')
    assert all(any(keyword in msg for keyword in banned_statements) for msg in messages)


@pytest.mark.parametrize('banned_statements, passes', [
    ([], True),
    (['GO TO'], False),
    (['GO TO', 'RETURN'], False),
    (['RETURN'], True)])
def test_banned_statements_config(banned_statements, passes):
    '''Test for banned statements with custom config.'''
    fcode = """
subroutine banned_statements()
integer :: dummy

dummy = 5
call foobar(dummy)
go to 100
print *, dummy
100 continue
end subroutine banned_statements
    """
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    config = {'BannedStatementsRule': {'banned': banned_statements}}
    _ = run_linter(source, [rules.BannedStatementsRule], config=config, handlers=[handler])

    assert len(messages) == (0 if passes else 1)
    keywords = ('BannedStatementsRule', 'GO TO', '[4.11]')
    assert all(all(keyword in msg for keyword in keywords) for msg in messages)
