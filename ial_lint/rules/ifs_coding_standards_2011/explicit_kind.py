# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import (
    FindNodes, ExpressionFinder, ExpressionRetriever, BasicType, ir
)
from loki.lint import GenericRule, RuleType
from loki.expression import symbols as sym


__all__ = ['ExplicitKindRule']


class ExplicitKindRule(GenericRule):  # Coding standards 4.7

    type = RuleType.SERIOUS

    docs = {
        'id': '4.7',
        'title': ('Variables and constants must be declared with explicit kind, using the kinds '
                  'defined in "PARKIND1" and "PARKIND2".'),
    }

    config = {
        'declaration_types': ['INTEGER', 'REAL'],
        'constant_types': ['REAL'],  # Coding standards document includes INTEGERS here
        'allowed_type_kinds': {
            'INTEGER': ['JPIM', 'JPIT', 'JPIB', 'JPIA', 'JPIS', 'JPIH'],
            'REAL': ['JPRB', 'JPRM', 'JPRS', 'JPRT', 'JPRH', 'JPRD', 'JPHOOK']
        }
    }

    @staticmethod
    def check_kind_declarations(subroutine, types, allowed_type_kinds, rule_report):
        '''Helper function that carries out the check for explicit kind specification
        on all declarations.
        '''
        for decl in FindNodes(ir.VariableDeclaration).visit(subroutine.spec):
            decl_type = decl.symbols[0].type
            if decl_type.dtype in types:
                if not decl_type.kind:
                    # Declared without any KIND specification
                    msg = f'{", ".join(str(var) for var in decl.symbols)} without explicit KIND declared'
                    rule_report.add(msg, decl)
                elif allowed_type_kinds.get(decl_type.dtype):
                    if decl_type.kind not in allowed_type_kinds[decl_type.dtype]:
                        # We have a KIND but it does not match any of the allowed kinds
                        msg = (f'{decl_type.kind!s} is not an allowed KIND value for '
                               f'{", ".join(str(var) for var in decl.symbols)}')
                        rule_report.add(msg, decl)

    @staticmethod
    def check_kind_literals(subroutine, types, allowed_type_kinds, rule_report):
        '''Helper function that carries out the check for explicit kind specification
        on all literals.
        '''

        class FindLiteralsWithKind(ExpressionFinder):
            """
            Custom expression finder that that yields all literals of the types
            specified in the config and stops recursion on loop ranges and array subscripts
            (to avoid warnings about integer constants in these cases)
            """

            retriever = ExpressionRetriever(
                query=lambda e: isinstance(e, types),
                recurse_query=lambda e: not isinstance(e, (sym.Array, sym.Range))
            )

        for node, exprs in FindLiteralsWithKind(unique=False, with_ir_node=True).visit(subroutine.ir):
            for literal in exprs:
                if not literal.kind:
                    rule_report.add(f'{literal} used without explicit KIND', node)
                elif allowed_type_kinds.get(literal.__class__):
                    if str(literal.kind).upper() not in allowed_type_kinds[literal.__class__]:
                        msg = f'{literal.kind} is not an allowed KIND value for {literal}'
                        rule_report.add(msg, node)

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        '''Check for explicit kind information in constants and
        variable declarations.
        '''
        # 1. Check variable declarations for explicit KIND
        #
        # When we check variable type information, we have BasicType values to identify
        # whether a variable is REAL, INTEGER, ... Therefore, we create a map that uses
        # the corresponding BasicType values as keys to look up allowed kinds for each type.
        # Since the case does not matter, we convert all allowed type kinds to upper case.
        types = tuple(BasicType.from_str(name) for name in config['declaration_types'])
        allowed_type_kinds = {}
        if config.get('allowed_type_kinds'):
            allowed_type_kinds = {BasicType.from_str(name): [kind.upper() for kind in kinds]
                                  for name, kinds in config['allowed_type_kinds'].items()}

        cls.check_kind_declarations(subroutine, types, allowed_type_kinds, rule_report)

        # 2. Check constants for explicit KIND
        #
        # Constants are represented by an instance of some Literal class, which directly
        # gives us their type. Therefore, we create a map that uses the corresponding
        # Literal types as keys to look up allowed kinds for each type. Again, we
        # convert all allowed type kinds to upper case.
        type_map = {'INTEGER': sym.IntLiteral, 'REAL': sym.FloatLiteral,
                    'LOGICAL': sym.LogicLiteral, 'CHARACTER': sym.StringLiteral}
        types = tuple(type_map[name] for name in config['constant_types'])
        if config.get('allowed_type_kinds'):
            allowed_type_kinds = {type_map[name]: [kind.upper() for kind in kinds]
                                  for name, kinds in config['allowed_type_kinds'].items()}

        cls.check_kind_literals(subroutine, types, allowed_type_kinds, rule_report)
