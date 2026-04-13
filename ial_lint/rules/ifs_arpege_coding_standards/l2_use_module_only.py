# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import ir, FindNodes
from loki.lint import GenericRule, RuleType


__all__ = ['QualifiedModuleImportsRule']


class QualifiedModuleImportsRule(GenericRule):
    """
    Checks that imports from modules via the USE statement are always
    fully qualified via a USE statement.
    """

    type = RuleType.SERIOUS

    fixable = False

    docs = {
        'id': 'L2',
        'title': (
            'Module imports via the USE statement shall contain an ONLY specifier.'
        ),
    }

    @classmethod
    def get_unqualified_imports(cls, ir_):
        """
        Check for unqualified ``Import`` statements.
        """
        return tuple(
            imp for imp in FindNodes(ir.Import).visit(ir_)
            if not imp.f_include and not imp.c_import and not imp.symbols
        )

    @classmethod
    def check_module(cls, module, rule_report, config):
        """
        Check for unqualified ``Import`` statements in ``Module`` units.
        """
        for imp in cls.get_unqualified_imports(module.spec):
            rule_report.add(f'Unqualified module import found :: {imp.module} :: )', module)

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        """
        Check for unqualified ``Import`` statements in ``Subroutine`` units.
        """
        for imp in cls.get_unqualified_imports(subroutine.spec):
            rule_report.add(f'Unqualified module import found :: {imp.module} :: )', subroutine)
