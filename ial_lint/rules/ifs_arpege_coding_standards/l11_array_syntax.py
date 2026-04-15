# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import FindNodes, ir
from loki.expression import symbols as sym
from loki.lint import GenericRule, RuleType


__all__ = ['ForbiddenArraySyntaxRule']


class ForbiddenArraySyntaxRule(GenericRule):
    """
    Fortran array syntax is forbidden except for trivial initialization and copy.
    """

    type = RuleType.SERIOUS

    docs = {
        'id': 'L11',
        'title': 'Fortran array syntax is forbidden except for trivial initialization and copy.'
    }

    @staticmethod
    def is_array_section(expr):
        return isinstance(expr, sym.Array) and any(isinstance(dim, sym.RangeIndex) for dim in expr.dimensions)

    @classmethod
    def get_array_sections(cls, expr):
        if cls.is_array_section(expr):
            return [expr]

        sections = []
        for child in getattr(expr, 'children', ()):
            sections.extend(cls.get_array_sections(child))
        return sections

    @classmethod
    def is_allowed_rhs(cls, expr):
        if isinstance(expr, sym.Array):
            return cls.is_array_section(expr)

        return not cls.get_array_sections(expr)

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        for assignment in FindNodes(ir.Assignment).visit(subroutine.body):
            if not cls.is_array_section(assignment.lhs):
                continue

            if cls.is_allowed_rhs(assignment.rhs):
                continue

            msg = 'Forbidden array syntax assignment'
            rule_report.add(msg, assignment)
