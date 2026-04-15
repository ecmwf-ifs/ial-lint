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


def test_l11_report_forbidden_array_syntax_assignments():
    fcode = """
subroutine l11_test(a, b, c, i, p)
  implicit none
  integer, intent(inout) :: a(:)
  integer, intent(in) :: b(:), c(:)
  integer, intent(in) :: i, p

  a(:) = 0
  a(:) = p
  a(:) = b(:)
  a(2:) = c(2:)
  a(i) = b(i)

  a(:) = b(:) + c(:)
  a(:) = 2 * b(:)
  a(2:) = b(2:) + c(2:)
end subroutine l11_test
    """.strip()
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.ForbiddenArraySyntaxRule], handlers=[handler])

    expected_messages = (
        ('[L11]', 'ForbiddenArraySyntaxRule', 'Forbidden array syntax assignment', '(l. 13)'),
        ('[L11]', 'ForbiddenArraySyntaxRule', 'Forbidden array syntax assignment', '(l. 14)'),
        ('[L11]', 'ForbiddenArraySyntaxRule', 'Forbidden array syntax assignment', '(l. 15)'),
    )

    assert len(messages) == len(expected_messages)
    for keywords in expected_messages:
        assert any(all(keyword in msg for keyword in keywords) for msg in messages)
