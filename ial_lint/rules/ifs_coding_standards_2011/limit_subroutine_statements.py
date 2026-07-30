# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import FindNodes, ir
from loki.lint import GenericRule, RuleType


__all__ = ['LimitSubroutineStatementsRule']


class LimitSubroutineStatementsRule(GenericRule):  # Coding standards 2.2

    type = RuleType.WARN

    docs = {
        'id': '2.2',
        'title': 'Subroutines should have no more than {max_num_statements} executable statements.',
    }

    config = {
        'max_num_statements': 300
    }

    # List of nodes that are considered executable statements
    exec_nodes = (
        ir.Assignment, ir.MaskedStatement, ir.GenericStmt, ir.Allocation,
        ir.Deallocation, ir.Nullify, ir.CallStatement
    )

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        '''
        Count the number of nodes in the subroutine and check if they
        exceed a given maximum number.
        '''
        # Count total number of executable nodes
        nodes = FindNodes(cls.exec_nodes).visit(subroutine.ir)
        num_nodes = len(nodes)

        # Subtract number of non-exec intrinsic nodes
        intrinsic_nodes = filter(lambda node: isinstance(node, (ir.FormatStmt, ir.PrintStmt)), nodes)
        num_nodes -= len(list(intrinsic_nodes))

        if num_nodes > config['max_num_statements']:
            msg = (f'Subroutine has {num_nodes} executable statements '
                   f'(should not have more than {config["max_num_statements"]})')
            rule_report.add(msg, subroutine)
