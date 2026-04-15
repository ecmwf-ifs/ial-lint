# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import FindNodes, ir
from loki.expression import symbols as sym
from loki.lint import GenericRule, RuleType


__all__ = ['CopyingAllocatableArraysRule']


class CopyingAllocatableArraysRule(GenericRule):
    """
    Allocatable arrays shall not be copied without explicit dimensions.
    """

    type = RuleType.SERIOUS

    docs = {
        'id': 'L8',
        'title': 'Allocatable arrays shall not be copied without explicit dimensions.'
    }

    @staticmethod
    def is_whole_array_reference(expr):
        return isinstance(expr, sym.Array) and expr.dimensions == ()

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        for assignment in FindNodes(ir.Assignment).visit(subroutine.body):
            if not cls.is_whole_array_reference(assignment.lhs):
                continue

            if not assignment.lhs.type.allocatable:
                continue

            if not cls.is_whole_array_reference(assignment.rhs):
                continue

            msg = 'Allocatable array copy requires explicit dimensions'
            rule_report.add(msg, assignment)
