# SPDX-FileCopyrightText: 2026 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileComment: In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import re

from pymbolic.primitives import Expression

from loki import (
    Visitor, ExpressionRetriever, Node, flatten, strip_inline_comments
)
from loki.lint import GenericRule, RuleType
from loki.expression import symbols as sym


__all__ = ['Fortran90OperatorsRule']


class Fortran90OperatorsRule(GenericRule):  # Coding standards 4.15

    type = RuleType.WARN

    docs = {
        'id': '4.15',
        'title': 'Use Fortran 90 comparison operators.'
    }

    fixable = True

    '''
    Regex patterns for each operator that match F77 and F90 operators as
    named groups, thus allowing to easily find out which operator was used.
    '''
    _op_patterns = {
        '==': re.compile(r'(?P<f77>\.eq\.)|(?P<f90>==)', re.I),
        '!=': re.compile(r'(?P<f77>\.ne\.)|(?P<f90>/=)', re.I),
        '>=': re.compile(r'(?P<f77>\.ge\.)|(?P<f90>>=)', re.I),
        '<=': re.compile(r'(?P<f77>\.le\.)|(?P<f90><=)', re.I),
        '>': re.compile(r'(?P<f77>\.gt\.)|(?P<f90>>(?!=))', re.I),
        '<': re.compile(r'(?P<f77>\.lt\.)|(?P<f90><(?!=))', re.I),
    }

    _op_map = {
        '==': '.eq.',
        '/=': '.ne.',
        '>=': '.ge.',
        '<=': '.le.',
        '>': '.gt.',
        '<': '.lt.'
    }

    class ComparisonRetriever(Visitor):
        """
        Bespoke expression retriever that extracts 3-tuples containing
        ``(node, expression root, comparison)`` for all :any:`Comparison` nodes.
        """

        retriever = ExpressionRetriever(lambda e: isinstance(e, sym.Comparison))

        def visit_Node(self, o, **kwargs):
            """
            Generic visitor method that will call the :any:`ExpressionRetriever`
            only on :class:`pymbolic.primitives.Expression` children, collecting
            ``(node, expression root, comparison)`` tuples for all matches.
            """
            retval = ()
            for ch in flatten(o.children):
                if isinstance(ch, Expression):
                    comparisons = self.retriever.retrieve(ch)
                    if comparisons:
                        retval += ((o, ch, comparisons),)
                elif isinstance(ch, Node):
                    retval += self.visit(ch, **kwargs)
            return retval

        def visit_tuple(self, o, **kwargs):
            """
            Specialized handling of tuples to concatenate the nested tuples
            returned by :meth:`visit_Node`.
            """
            retval = ()
            for ch in o:
                if ch is not None:
                    retval += self.visit(ch, **kwargs)
            return retval

        visit_list = visit_tuple

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        '''Check for the use of Fortran 90 comparison operators.'''
        # Use the bespoke visitor to retrieve all comparison nodes alongside with their expression root
        # and the IR node they belong to
        for node, expr_root, expr_list in cls.ComparisonRetriever().visit(subroutine.ir):
            # Use the string representation of the expression to find the source line
            lstart, lend = node.source.find(str(expr_root))
            lines = node.source.clone_lines((lstart, lend))

            # For each comparison operator, use the original source code (because the frontends always
            # translate them to F90 operators) to check if F90 or F77 operators were used
            for op in sorted({op.operator for op in expr_list}):
                # find source line for operator
                op_str = op if op != '!=' else '/='
                line = [line for line in lines if op_str in strip_inline_comments(line.string)]
                if not line:
                    line = [line for line in lines
                            if op_str in strip_inline_comments(line.string.replace(cls._op_map[op_str], op_str))]

                source_string = strip_inline_comments(line[0].string)
                matches = cls._op_patterns[op].findall(source_string)
                for f77, _ in matches:
                    if f77:
                        msg = f'Use Fortran 90 comparison operator "{op_str}" instead of "{f77}"'
                        rule_report.add(msg, node)

    @classmethod
    def fix_subroutine(cls, subroutine, rule_report, config):
        '''Replace by Fortran 90 comparison operators.'''
        # We only have to invalidate the source string for the expression. This will cause the
        # backend to regenerate the source string for that node and use Fortran 90 operators
        # automatically
        mapper = {}
        for report in rule_report.problem_reports:
            new_expr = report.location
            new_expr.update_metadata({'source': None})
            mapper[report.location] = new_expr
        return mapper
