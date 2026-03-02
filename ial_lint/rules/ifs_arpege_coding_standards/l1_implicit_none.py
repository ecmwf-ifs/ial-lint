# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import re

from loki import ir, FindNodes, Module
from loki.lint import GenericRule, RuleType


__all__ = ['MissingImplicitNoneRule']


class MissingImplicitNoneRule(GenericRule):
    """
    ``IMPLICIT NONE`` must be present in all scoping units but may be omitted
    in module procedures.
    """

    type = RuleType.SERIOUS

    docs = {
        'id': 'L1',
        'title': (
            'IMPLICIT NONE must figure in all scoping units. '
            'Once per module is sufficient.'
        ),
    }

    _regex = re.compile(r'implicit\s+none\b', re.I)

    @classmethod
    def check_for_implicit_none(cls, ir_):
        """
        Check for intrinsic nodes that match the regex.
        """
        for intr in FindNodes(ir.Intrinsic).visit(ir_):
            if cls._regex.match(intr.text):
                break
        else:
            return False
        return True

    @classmethod
    def check_module(cls, module, rule_report, config):
        """
        Check for ``IMPLICIT NONE`` in the module's spec.
        """
        found_implicit_none = cls.check_for_implicit_none(module.spec)
        if not found_implicit_none:
            # No 'IMPLICIT NONE' intrinsic node was found
            rule_report.add('No `IMPLICIT NONE` found', module)

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        """
        Check for ``IMPLICIT NONE`` in the subroutine's spec or an enclosing
        :any:`Module` scope.
        """
        found_implicit_none = cls.check_for_implicit_none(subroutine.ir)

        # Check if enclosing scopes contain implicit none
        scope = subroutine.parent
        while scope and not found_implicit_none:
            if isinstance(scope, Module) and hasattr(scope, 'spec') and scope.spec:
                found_implicit_none = cls.check_for_implicit_none(scope.spec)
            scope = scope.parent if hasattr(scope, 'parent') else None

        if not found_implicit_none:
            # No 'IMPLICIT NONE' intrinsic node was found
            rule_report.add('No `IMPLICIT NONE` found', subroutine)
