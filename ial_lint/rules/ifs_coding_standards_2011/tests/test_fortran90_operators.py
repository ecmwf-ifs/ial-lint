# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import Sourcefile
from loki.lint import DefaultHandler

from conftest import run_linter

from ial_lint.rules import ifs_coding_standards_2011 as rules


def test_fortran_90_operators():
    '''Test for existence of non Fortran 90 comparison operators.'''
    fcode = """
subroutine test_routine(ia, ib, ic)
integer, intent(in) :: ia, ib, ic

! This should produce 6 problems (one for each operator)
do while (ia .ge. 3 .or. ia .le. -7)
  if (ib .gt. 5 .or. ib .lt. -1) then
    if (ic .eq. 4 .and. ib .ne. -2) then
      print *, 'Foo'
    end if
  end if
end do

! This should produce no problems
do while (ia >= 3 .or. ia <= -7)
  if (ib > 5 .or. ib < -1) then
    if (ic == 4 .and. ib /= -2) then
      print *, 'Foo'
    end if
  end if
end do

! This should report 5 problems
do while (ia >= 3 .or. & ! This <= should not cause confusion
          ia .le. -7)
  if (ib .gt. 5 .or. ib <= -1) then
    if (ic .gt. 4 .and. ib == -2) then
      print *, 'Foo'
    end if
  elseif (ib .eq. 5) then
    print *, 'Bar'
  else
    if (ic .gt. 2) print *, 'Baz'
  end if
end do
end subroutine test_routine
    """.strip()
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    _ = run_linter(source, [rules.Fortran90OperatorsRule], handlers=[handler])

    assert len(messages) == 11
    keywords = ('Fortran90OperatorsRule', '[4.15]', 'Use Fortran 90 comparison operator')
    assert all(all(keyword in msg for keyword in keywords) for msg in messages)

    # Check that violations are reported in the right order
    f77_f90_line = (
        ('.le.', '<=', '5'),
        ('.ge.', '>=', '5'),
        ('.lt.', '<', '6'),
        ('.gt.', '>', '6'),
        ('.ne.', '/=', '7'),
        ('.eq.', '==', '7'),
        ('.le.', '<=', '23'),
        ('.gt.', '>', '25'),
        ('.gt.', '>', '26'),
        ('.eq.', '==', '29'),
        ('.gt.', '>', '32'),
    )

    for keywords, message in zip(f77_f90_line, messages):
        assert all(str(keyword) in message for keyword in keywords)
