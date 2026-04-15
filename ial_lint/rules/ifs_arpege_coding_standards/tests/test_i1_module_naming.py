# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from pathlib import Path

from loki import Sourcefile
from loki.lint import DefaultHandler

from conftest import run_linter

from ial_lint.rules import ifs_arpege_coding_standards as rules


def test_i1_module_naming():
    fcode = """
module module_naming_mod
contains
  subroutine sub_ok
  end subroutine sub_ok
end module module_naming_mod

module MODULE_NAMING_UPPERCASE_MOD
contains
  subroutine sub_upper
  end subroutine sub_upper
end module MODULE_NAMING_UPPERCASE_MOD

module module_naming
end module module_naming
    """.strip()
    source = Sourcefile.from_source(fcode)
    for module in source.modules:
        module.source.file = str(Path(__file__).parent / 'module_naming_mod.F90')

    messages = []
    handler = DefaultHandler(target=messages.append)
    run_linter(source, [rules.ModuleNamingRule], handlers=[handler])

    expected_messages = (
        ('[I1]', 'ModuleNamingRule', 'filename', 'module_naming_mod.F90', 'MODULE_NAMING_UPPERCASE_MOD'),
        ('[I1]', 'ModuleNamingRule', 'should end with "_mod"', 'module_naming'),
        ('[I1]', 'ModuleNamingRule', 'filename', 'module_naming_mod.F90', 'module_naming'),
    )

    assert len(messages) == len(expected_messages)
    for keywords in expected_messages:
        assert any(all(keyword in msg for keyword in keywords) for msg in messages)
