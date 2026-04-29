# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import FindNodes, ir
from loki.lint import GenericRule, RuleType


__all__ = ['BannedStatementsRule']


class BannedStatementsRule(GenericRule):  # Coding standards 4.11

    type = RuleType.WARN

    docs = {
        'id': '4.11',
        'title': 'Banned statements.',
    }

    config = {
        'banned': ['STOP', 'PRINT', 'RETURN', 'ENTRY', 'DIMENSION',
                   'DOUBLE PRECISION', 'COMPLEX', 'GO TO', 'CONTINUE',
                   'FORMAT', 'COMMON', 'EQUIVALENCE'],
    }

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        '''Check for banned statements in intrinsic nodes.'''
        for intr in FindNodes(ir.GenericStmt).visit(subroutine.ir):
            # Get the keyword of individual statement nodes
            keyword = intr.keyword if intr.keyword else intr.text.split(' ')[0]
            if keyword.upper() in config['banned']:
                rule_report.add(f'Banned keyword "{keyword}"', intr)

        # Note, the DIMENSION keyword is handled as a declaration attribute in Loki
        for decl in FindNodes(ir.VariableDeclaration).visit(subroutine.spec):
            if decl.dimensions:
                rule_report.add('Banned keyword DIMENSION', decl)
