# SPDX-FileCopyrightText: 2026 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileComment: In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import FindNodes, ir
from loki.lint import GenericRule, RuleType


__all__ = ['MplCdstringRule']


class MplCdstringRule(GenericRule):  # Coding standards 3.12

    type = RuleType.SERIOUS

    docs = {
        'id': '3.12',
        'title': 'Calls to MPL subroutines should provide a "CDSTRING" identifying the caller.',
    }

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        '''Check all calls to MPL subroutines for a CDSTRING.'''
        for call in FindNodes(ir.CallStatement).visit(subroutine.ir):
            if str(call.name).upper().startswith('MPL_'):
                for kw, _ in call.kwarguments:
                    if kw.upper() == 'CDSTRING':
                        break
                else:
                    msg = f'No "CDSTRING" provided in call to {call.name}'
                    rule_report.add(msg, call)
