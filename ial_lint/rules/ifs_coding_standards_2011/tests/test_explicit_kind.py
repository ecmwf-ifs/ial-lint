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


def test_explicit_kind(rules):
    fcode = """
subroutine routine_okay
use some_type_module, only : jpim, jprb
integer(kind=jpim) :: i, j
real(kind=jprb) :: a(3), b

i = 1_JPIM + 7_JPIM
j = 2_JPIM
a(1:3) = 3._JPRB
b = 4.0_JPRB
do j=1,3
    a(j) = real(j)
end do
end subroutine routine_okay

subroutine routine_not_okay
integer :: i
integer(kind=1) :: j
real :: a(3)
real(kind=8) :: b

i = 1 + 7
j = 2
a(1:3) = 3e0
b = 4.0 + 5d0 + 6._4
end subroutine routine_not_okay
    """.strip()
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    # Need to include INTEGER constants in config as (temporarily) removed from defaults
    config = {'ExplicitKindRule': {'constant_types': ['REAL', 'INTEGER']}}
    _ = run_linter(source, [rules.ExplicitKindRule], config=config, handlers=[handler])

    # Note: This creates one message too many, namely the literal '4' in the constant
    # 6._4. This is because we represent the kind parameter as an expression (which can be
    # an imported name, for example). Since '4' (or any other literals) are not allowed kind
    # values in IFS this should not be a problem in practice: it will simply create an
    # additional spurious error in that case
    assert len(messages) == 12
    assert all('[4.7]' in msg for msg in messages)
    assert all('ExplicitKindRule' in msg for msg in messages)

    # Keywords to search for in the messages as tuples:
    # ('var name' or 'literal', 'line number', 'invalid kind value' or None)
    keywords = (
        # Declarations
        ('i', '16', None), ('j', '17', '1'), ('a(3)', '18', None), ('b', '19', '8'),
        # Literals
        ('1', '21', None), ('7', '21', None), ('2', '22', None), ('3e0', '23', None),
        ('4.0', '24', None), ('5d0', '24', None), ('4', '24', None), ('6._4', '24', '4')
    )
    for keys, msg in zip(keywords, messages):
        assert all(kw in msg for kw in keys if kw is not None)
