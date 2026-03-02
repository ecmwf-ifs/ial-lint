# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import re

from loki import FindNodes, ir
from loki.lint import GenericRule, RuleType


__all__ = ['ImplicitNoneRule']


class ImplicitNoneRule(GenericRule):  # Coding standards 4.4

    type = RuleType.SERIOUS

    docs = {
        'id': '4.4',
        'title': '"IMPLICIT NONE" is mandatory in all routines.',
    }

    _regex = re.compile(r'implicit\s+none\b', re.I)

    @staticmethod
    def check_for_implicit_none(ast):
        """
        Check for intrinsic nodes that match the regex.
        """
        for intr in FindNodes(ir.Intrinsic).visit(ast):
            if ImplicitNoneRule._regex.match(intr.text):
                break
        else:
            return False
        return True

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        """
        Check for IMPLICIT NONE in the subroutine's spec or any enclosing
        scope.
        """
        found_implicit_none = cls.check_for_implicit_none(subroutine.ir)

        # Check if enclosing scopes contain implicit none
        scope = subroutine.parent
        while scope and not found_implicit_none:
            if hasattr(scope, 'spec') and scope.spec:
                found_implicit_none = cls.check_for_implicit_none(scope.spec)
            scope = scope.parent if hasattr(scope, 'parent') else None

        if not found_implicit_none:
            # No 'IMPLICIT NONE' intrinsic node was found
            rule_report.add('No "IMPLICIT NONE" found', subroutine)
