# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import BasicType, FindNodes, ir
from loki.lint import GenericRule, RuleType


__all__ = ['KindSpecificationRule']


class KindSpecificationRule(GenericRule):
    """
    INTEGER and REAL variables shall have an explicit KIND specification.

    This initial I2 implementation checks declarations only and does not yet
    validate numeric literals.
    """

    type = RuleType.SERIOUS

    docs = {
        'id': 'I2',
        'title': 'INTEGER and REAL variables shall use explicit KIND values from PARKIND-like definitions.'
    }

    config = {
        'declaration_types': ['INTEGER', 'REAL'],
        'allowed_type_kinds': {
            'INTEGER': ['JPIM', 'JPIT', 'JPIB', 'JPIA', 'JPIS', 'JPIH'],
            'REAL': ['JPRB', 'JPRM', 'JPRS', 'JPRT', 'JPRH', 'JPRD', 'JPHOOK']
        }
    }

    @classmethod
    def check_kind_declarations(cls, spec, types, allowed_type_kinds, rule_report):
        for decl in FindNodes(ir.VariableDeclaration).visit(spec):
            decl_type = decl.symbols[0].type
            if decl_type.dtype not in types:
                continue

            if not decl_type.kind:
                msg = f'{", ".join(str(var) for var in decl.symbols)} declared without explicit KIND'
                rule_report.add(msg, decl)
                continue

            allowed_kinds = allowed_type_kinds.get(decl_type.dtype)
            if allowed_kinds and str(decl_type.kind).upper() not in allowed_kinds:
                msg = (f'{decl_type.kind!s} is not an allowed KIND value for '
                       f'{", ".join(str(var) for var in decl.symbols)}')
                rule_report.add(msg, decl)

    @classmethod
    def check_module(cls, module, rule_report, config):
        types = tuple(BasicType.from_str(name) for name in config['declaration_types'])
        allowed_type_kinds = {
            BasicType.from_str(name): [kind.upper() for kind in kinds]
            for name, kinds in config['allowed_type_kinds'].items()
        }
        cls.check_kind_declarations(module.spec, types, allowed_type_kinds, rule_report)

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        types = tuple(BasicType.from_str(name) for name in config['declaration_types'])
        allowed_type_kinds = {
            BasicType.from_str(name): [kind.upper() for kind in kinds]
            for name, kinds in config['allowed_type_kinds'].items()
        }
        cls.check_kind_declarations(subroutine.spec, types, allowed_type_kinds, rule_report)
