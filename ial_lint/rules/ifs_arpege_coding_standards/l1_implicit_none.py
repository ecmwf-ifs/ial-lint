# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import ir, FindNodes, Transformer
from loki.lint import GenericRule, RuleType


__all__ = ['MissingImplicitNoneRule']


class MissingImplicitNoneRule(GenericRule):
    """
    ``IMPLICIT NONE`` must be present in all scoping units but may be omitted
    in module procedures.
    """

    type = RuleType.SERIOUS

    fixable = True

    docs = {
        'id': 'L1',
        'title': (
            'IMPLICIT NONE must figure in all scoping units. '
            'Once per module is sufficient.'
        ),
    }

    @classmethod
    def check_for_implicit_none(cls, ir_):
        """
        Check for ``IMPLICIT NONE`` in a given IR tree.
        """
        for intr in FindNodes(ir.ImplicitStmt).visit(ir_):
            if intr.text == 'NONE':
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
            rule_report.add('No `IMPLICIT NONE` found', module)

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        """
        Check for ``IMPLICIT NONE`` in the subroutine's spec or an enclosing
        :any:`Module` scope.
        """
        found_here = cls.check_for_implicit_none(subroutine.ir)

        # Check if any of the enclosing parent scopes contain implicit none
        found_in_parent = any(cls.check_for_implicit_none(parent.spec) for parent in subroutine.parents)

        if not found_here and not found_in_parent:
            rule_report.add('No `IMPLICIT NONE` found', subroutine)

        if found_here and found_in_parent:
            rule_report.add('Redundant `IMPLICIT NONE` found', subroutine)

    @classmethod
    def fix_module(cls, module, rule_report, config):
        """
        Check for ``IMPLICIT NONE`` in the module's spec.
        """

        if not cls.check_for_implicit_none(module.spec):
            # Find index between imports and declarations in spec
            imports = FindNodes(ir.Import).visit(module.spec)
            idx = module.spec.body.index(imports[-1]) + 1 if imports else 0
            module.spec = module.spec or ir.Section()
            module.spec.insert(idx, ir.ImplicitStmt())

            # Ensure that the string for the spec region is re-created
            if module.spec.source:
                module.spec.source.invalidate(children=True)
            module.source.invalidate(children=True)

        # Recurse into subroutines
        for routine in module.subroutines:
            cls.fix_subroutine(routine, rule_report, config)

    @classmethod
    def fix_subroutine(cls, subroutine, rule_report, config):
        """
        Insert missing ``IMPLICIT NONE`` or remove redundant ones.
        """
        found_here = cls.check_for_implicit_none(subroutine.ir)

        found_in_parent = any(cls.check_for_implicit_none(parent.spec) for parent in subroutine.parents)
        mapper = {}

        if found_here and found_in_parent:
            # Find redundant `ImplicitStmt` and remove via mapper
            mapper = {i: None for i in FindNodes(ir.ImplicitStmt).visit(subroutine.spec) if i.text == 'NONE'}
            subroutine.spec = Transformer(mapper).visit(subroutine.spec)

            if subroutine.spec.source:
                subroutine.spec.source.invalidate(children=True)
            subroutine.source.invalidate(children=True)

            subroutine.parent.source.invalidate(children=True)
            if subroutine.parent.contains.source:
                subroutine.parent.contains.source.invalidate(children=True)

        if not found_here and not found_in_parent:
            # Find index between imports and declarations in spec
            imports = FindNodes(ir.Import).visit(subroutine.spec)
            idx = (subroutine.spec.body.index(imports[-1]) + 1) if imports else 0
            subroutine.spec.insert(idx, ir.ImplicitStmt())

            # Ensure that the string for the spec region is re-created
            if subroutine.spec.source:
                subroutine.spec.source.invalidate()

        # Recurse into internal subroutines
        for child in subroutine.subroutines:
            cls.fix_subroutine(child, rule_report, config)
