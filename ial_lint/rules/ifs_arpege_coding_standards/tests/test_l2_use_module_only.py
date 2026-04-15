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


def test_l2_report_unqualified_imports():
    fcode = """
module l2_mod
  use mod_a
  use mod_b, only: x
  implicit none
#include "foo.intfb.h"
contains

  subroutine l2_sub()
    use mod_c
    use mod_d, only: y
    implicit none
#include "bar.func.h"

  end subroutine l2_sub
end module l2_mod
    """.strip()
    source = Sourcefile.from_source(fcode)
    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.QualifiedModuleImportsRule], handlers=[handler])

    expected_messages = (
        ('[L2]', 'QualifiedModuleImportsRule', 'Unqualified module import found', 'mod_a', '(l. 1)'),
        ('[L2]', 'QualifiedModuleImportsRule', 'Unqualified module import found', 'mod_c', '(l. 8)'),
    )

    assert len(messages) == len(expected_messages)
    for keywords in expected_messages:
        assert any(all(keyword in msg for keyword in keywords) for msg in messages)
