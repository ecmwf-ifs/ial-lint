# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from pathlib import Path

from loki import BasicType
from loki.lint import GenericRule, RuleType


__all__ = ['ModuleNamingRule', 'VariableNamingRule']


class ModuleNamingRule(GenericRule):
    """
    Check the non-semantic I1 module naming conventions.

    This only checks the local, objective subset of I1: module names ending in
    ``_mod`` and matching the source filename. Semantic naming conventions for
    routines and suffix conventions are intentionally not checked here.
    """

    type = RuleType.SERIOUS

    docs = {
        'id': 'I1',
        'title': 'Module names should end with "_mod" and match the source filename.'
    }

    @classmethod
    def check_module(cls, module, rule_report, config):
        if not module.name.lower().endswith('_mod'):
            msg = f'Module name "{module.name}" should end with "_mod"'
            rule_report.add(msg, module)

        if module.source.file:
            path = Path(module.source.file)
            if module.name.lower() != path.stem.lower():
                msg = f'Module filename "{path.name}" does not match module name "{module.name}"'
                rule_report.add(msg, module)


class VariableNamingRule(GenericRule):
    """
    Check the non-semantic I1 variable naming conventions.

    This only checks the local, objective subset of I1: dummy and local variable
    prefixes by type. Semantic naming conventions and suffix conventions are
    intentionally not checked here.
    """

    type = RuleType.SERIOUS

    docs = {
        'id': 'I1',
        'title': 'Dummy and local variables should follow the IFS-Arpege type prefix naming convention.'
    }

    dummy_prefixes = {
        BasicType.INTEGER: 'k',
        BasicType.REAL: 'p',
        BasicType.LOGICAL: 'ld',
    }

    local_prefixes = {
        BasicType.INTEGER: 'i',
        BasicType.REAL: 'z',
        BasicType.LOGICAL: 'll',
    }

    @classmethod
    def expected_prefix(cls, symbol, is_dummy):
        prefixes = cls.dummy_prefixes if is_dummy else cls.local_prefixes
        return prefixes.get(symbol.type.dtype, 'yd' if is_dummy else 'yl')

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        dummy_names = {arg.name.lower() for arg in subroutine.arguments}

        for decl in subroutine.declarations:
            for symbol in decl.symbols:
                if symbol.type.parameter:
                    continue

                is_dummy = symbol.name.lower() in dummy_names
                expected = cls.expected_prefix(symbol, is_dummy)
                if symbol.name.lower().startswith(expected):
                    continue

                scope = 'Dummy argument' if is_dummy else 'Local variable'
                msg = f'{scope} "{symbol.name}" should start with "{expected.upper()}"'
                rule_report.add(msg, decl)
