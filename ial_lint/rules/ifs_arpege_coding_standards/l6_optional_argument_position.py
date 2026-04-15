# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki.lint import GenericRule, RuleType


__all__ = ['OptionalArgumentPositionRule']


class OptionalArgumentPositionRule(GenericRule):
    """
    Optional arguments to a routine shall be after all non-optional ones.
    """

    type = RuleType.SERIOUS

    docs = {
        'id': 'L6',
        'title': 'Optional arguments to a routine shall be after non-optional ones.'
    }

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        found_optional = False

        for arg in subroutine.arguments:
            if arg.type.optional:
                found_optional = True
            elif found_optional:
                msg = f'Non-optional dummy argument after OPTIONAL one: {arg.name}'
                rule_report.add(msg, subroutine)
