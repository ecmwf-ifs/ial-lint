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


def test_l8_report_allocatable_array_copy_without_dimensions():
    fcode = """
subroutine l8_test(a, b, c, x, y, i, scalar)
  implicit none
  real, allocatable, intent(inout) :: a(:)
  real, allocatable, intent(in) :: b(:)
  real, intent(in) :: c(:), y(:)
  real, intent(inout) :: x(:)
  integer, intent(in) :: i
  real, intent(in) :: scalar

  a = b
  a = c
  a(:) = b(:)
  a(i) = b(i)
  x = y
  a = scalar
end subroutine l8_test
    """.strip()
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.CopyingAllocatableArraysRule], handlers=[handler])

    expected_messages = (
        ('[L8]', 'CopyingAllocatableArraysRule', 'Allocatable array copy requires explicit dimensions', '(l. 10)'),
        ('[L8]', 'CopyingAllocatableArraysRule', 'Allocatable array copy requires explicit dimensions', '(l. 11)'),
    )

    assert len(messages) == len(expected_messages)
    for keywords in expected_messages:
        assert any(all(keyword in msg for keyword in keywords) for msg in messages)
