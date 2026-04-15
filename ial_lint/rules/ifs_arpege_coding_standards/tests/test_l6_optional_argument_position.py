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


def test_l6_report_non_optional_after_optional():
    fcode = """
subroutine l6_ok(a, b, c)
  implicit none
  integer, intent(in) :: a
  integer, intent(in), optional :: b
  integer, intent(in), optional :: c
end subroutine l6_ok

subroutine l6_not_ok(a, b, c, d)
  implicit none
  integer, intent(in) :: a
  integer, intent(in), optional :: b
  integer, intent(in) :: c
  integer, intent(in), optional :: d
end subroutine l6_not_ok

subroutine l6_also_not_ok(a, b, c, d)
  implicit none
  integer, intent(in), optional :: a
  integer, intent(in) :: b
  integer, intent(in), optional :: c
  integer, intent(in) :: d
end subroutine l6_also_not_ok
    """.strip()
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.OptionalArgumentPositionRule], handlers=[handler])

    expected_messages = (
        ('[L6]', 'OptionalArgumentPositionRule', 'Non-optional dummy argument after OPTIONAL one: c', '(l. 8)'),
        ('[L6]', 'OptionalArgumentPositionRule', 'Non-optional dummy argument after OPTIONAL one: b', '(l. 16)'),
        ('[L6]', 'OptionalArgumentPositionRule', 'Non-optional dummy argument after OPTIONAL one: d', '(l. 16)'),
    )

    assert len(messages) == len(expected_messages)
    for keywords in expected_messages:
        assert any(all(keyword in msg for keyword in keywords) for msg in messages)
