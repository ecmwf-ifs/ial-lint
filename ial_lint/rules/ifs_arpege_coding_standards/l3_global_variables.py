# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki.lint import GenericRule, RuleType


__all__ = ['OnlyParameterGlobalVarRule']


class OnlyParameterGlobalVarRule(GenericRule):
    """
    Only parameters to be declared as global variables.
    """

    type = RuleType.SERIOUS

    docs = {
        'id': 'L3',
        'title': 'Only parameters to be declared as global variables.'
    }

    @classmethod
    def check_module(cls, module, rule_report, config):
        for decl in module.declarations:
            if not decl.symbols[0].type.parameter:
                msg = f'Global variable(s) declared that are not parameters: {", ".join(s.name for s in decl.symbols)}'
                rule_report.add(msg, decl)
