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


def test_i2_kind_specification_declarations():
    fcode = """
module i2_kind_mod
  use parkind1, only: jpim, jprb
  implicit none
  integer(kind=jpim) :: i_ok
  real(kind=jprb) :: r_ok
  integer :: i_missing
  real :: r_missing
  integer(kind=1) :: i_bad
  real(kind=8) :: r_bad
contains
  subroutine i2_kind_sub(k_ok, p_ok)
    use parkind1, only: jpim, jprb
    implicit none
    integer(kind=jpim), intent(in) :: k_ok
    real(kind=jprb), intent(inout) :: p_ok
    integer :: k_missing
    real :: p_missing
    integer(kind=1) :: k_bad
    real(kind=8) :: p_bad
  end subroutine i2_kind_sub
end module i2_kind_mod
    """.strip()
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.KindSpecificationRule], handlers=[handler])

    expected_messages = (
        ('[I2]', 'KindSpecificationRule', 'i_missing declared without explicit KIND', '(l. 6)'),
        ('[I2]', 'KindSpecificationRule', 'r_missing declared without explicit KIND', '(l. 7)'),
        ('[I2]', 'KindSpecificationRule', '1 is not an allowed KIND value for i_bad', '(l. 8)'),
        ('[I2]', 'KindSpecificationRule', '8 is not an allowed KIND value for r_bad', '(l. 9)'),
        ('[I2]', 'KindSpecificationRule', 'k_missing declared without explicit KIND', '(l. 16)'),
        ('[I2]', 'KindSpecificationRule', 'p_missing declared without explicit KIND', '(l. 17)'),
        ('[I2]', 'KindSpecificationRule', '1 is not an allowed KIND value for k_bad', '(l. 18)'),
        ('[I2]', 'KindSpecificationRule', '8 is not an allowed KIND value for p_bad', '(l. 19)'),
    )

    assert len(messages) == len(expected_messages)
    for keywords in expected_messages:
        assert any(all(keyword in msg for keyword in keywords) for msg in messages)
