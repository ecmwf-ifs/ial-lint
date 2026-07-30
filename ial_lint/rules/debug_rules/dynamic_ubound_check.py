# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import operator as _op
from loki import (
     FindNodes, RangeIndex, IntLiteral, as_tuple,
     SubstituteExpressions, Array, VariableDeclaration, flatten,
     FindInlineCalls, Conditional, FindExpressions, Comparison
)
from loki.lint import GenericRule, RuleType


__all__ = ['DynamicUboundCheckRule']


class DynamicUboundCheckRule(GenericRule):
    """
    Rule to check for run-time ubound checks for assumed shape dummy arguments
    """

    type = RuleType.WARN
    fixable = True

    @staticmethod
    def is_assumed_shape(arg):
        """
        Method to check if argument is an assumed shape array.
        """

        if all(isinstance(dim, RangeIndex) for dim in arg.shape):
            return all(dim.upper is None and dim.lower is None for dim in arg.shape)
        return False

    @staticmethod
    def get_ubound_checks(subroutine):
        """
        Method to return UBOUND checks nested within a :any:`Conditional`.
        """

        cond_map = {cond: FindInlineCalls(unique=False).visit(cond.condition)
                    for cond in FindNodes(Conditional).visit(subroutine.body)}
        return {call: cond for cond, calls in cond_map.items() for call in calls}

    @classmethod
    def get_assumed_shape_args(cls, subroutine):
        """
        Method to return all assumed-shape dummy arguments in a :any:`Subroutine`.
        """
        args = [arg for arg in subroutine.arguments if isinstance(arg, Array)]
        return [arg for arg in args if cls.is_assumed_shape(arg)]

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        """
        Method to check for run-time ubound checks for assumed shape dummy arguments
        """

        ubound_checks = cls.get_ubound_checks(subroutine)
        args = cls.get_assumed_shape_args(subroutine)

        for arg in args:
            checks = [c for c in ubound_checks if arg.name in c.arguments]
            params = flatten([p for c in checks for p in c.arguments if not p == arg])
            if all(IntLiteral(d+1) in params for d in range(len(arg.shape))):
                msg = f'Run-time UBOUND checks for assumed-shape arg: {arg}'
                rule_report.add(msg, subroutine)

    @classmethod
    def fix_subroutine(cls, subroutine, rule_report, config):
        """
        Method to fix run-time ubound checks for assumed shape dummy arguments
        """

        ubound_checks = cls.get_ubound_checks(subroutine)
        args = cls.get_assumed_shape_args(subroutine)

        node_map = {}
        var_map = {}

        for arg in args:
            checks = [c for c in ubound_checks if arg.name in c.arguments]
            params = {p: c for c in checks for p in c.arguments if not p == arg}

            # check if ubounds of all dimensions are tested
            if all(IntLiteral(d+1) in params for d in range(len(arg.shape))):
                new_shape = ()
                for d in range(len(arg.shape)):
                    conditional = ubound_checks[params[IntLiteral(d+1)]]
                    node_map[conditional] = None

                    # extract comparison expressions in case they are nested in a logical operation
                    conditions = [c for c in FindExpressions().visit(conditional.condition)
                                  if isinstance(c, Comparison)]
                    conditions = [c for c in conditions if c.operator in ('<', '>')]

                    cond = [c for c in conditions if arg.name in c and IntLiteral(d+1) in c][0]

                    # build ordered tuple for declaration shape
                    if 'ubound' in FindExpressions().visit(cond.left):
                        new_shape += as_tuple(cond.right)
                    else:
                        new_shape += as_tuple(cond.left)

                vtype = arg.type.clone(shape=new_shape)
                var_map.update({arg: arg.clone(type=vtype, dimensions=new_shape)})

        # update variable declarations
        subroutine.spec = SubstituteExpressions(var_map).visit(subroutine.spec)
        for decl in FindNodes(VariableDeclaration).visit(subroutine.spec):
            if decl.dimensions:
                if not all(sym.shape == decl.dimensions for sym in decl.symbols):
                    new_decls = as_tuple(VariableDeclaration(as_tuple(sym)) for sym in decl.symbols)
                    node_map.update({decl: new_decls})

        return node_map
