# SPDX-FileCopyrightText: 2026 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileComment: In applying this licence, ECMWF does not waive the privileges and immunities
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
            for keyword in config['banned']:
                if keyword.upper() in intr.text.upper() or keyword.upper() == intr.keyword:
                    rule_report.add(f'Banned keyword "{keyword}"', intr)
