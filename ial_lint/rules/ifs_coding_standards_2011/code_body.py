# SPDX-FileCopyrightText: 2026 European Centre for Medium-Range Weather Forecasts (ECMWF)
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileComment: In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import Visitor, flatten
from loki.lint import GenericRule, RuleType


__all__ = ['CodeBodyRule']


class CodeBodyRule(GenericRule):  # Coding standards 1.3

    type = RuleType.WARN

    docs = {
        'id': '1.3',
        'title': ('Rules for Code Body: '
                  'Nesting of conditional blocks should not be more than {max_nesting_depth} '
                  'levels deep;'),
    }

    config = {
        'max_nesting_depth': 3,
    }

    class NestingDepthVisitor(Visitor):

        @classmethod
        def default_retval(cls):
            return []

        def __init__(self, max_nesting_depth):
            super().__init__()
            self.max_nesting_depth = max_nesting_depth

        def visit(self, o, *args, **kwargs):
            return flatten(super().visit(o, *args, **kwargs))

        def visit_Conditional(self, o, **kwargs):
            level = kwargs.pop('level', 0)
            too_deep = []
            if level >= self.max_nesting_depth and not getattr(o, 'inline', False):
                too_deep = [o]
            too_deep += self.visit(o.body, level=level + 1, **kwargs)
            if o.has_elseif:
                too_deep += self.visit(o.else_body, level=level, **kwargs)
            else:
                too_deep += self.visit(o.else_body, level=level + 1, **kwargs)
            return too_deep

        def visit_MultiConditional(self, o, **kwargs):
            level = kwargs.pop('level', 0)
            too_deep = []
            if level >= self.max_nesting_depth and not getattr(o, 'inline', False):
                too_deep = [o]
            too_deep += self.visit(o.bodies, level=level + 1, **kwargs)
            too_deep += self.visit(o.else_body, level=level + 1, **kwargs)
            return too_deep

        visit_TypeConditional = visit_MultiConditional

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        '''Check the code body: Nesting of conditional blocks.'''
        too_deep = cls.NestingDepthVisitor(config['max_nesting_depth']).visit(subroutine.body)
        msg = f'Nesting of conditionals exceeds limit of {config["max_nesting_depth"]}'
        for node in too_deep:
            rule_report.add(msg, node)
