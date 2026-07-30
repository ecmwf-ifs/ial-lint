# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki.lint import GenericRule, RuleType


__all__ = ['MaxDummyArgsRule']


class MaxDummyArgsRule(GenericRule):  # Coding standards 3.6

    type = RuleType.INFO

    docs = {
        'id': '3.6',
        'title': 'Routines should have no more than {max_num_arguments} dummy arguments.',
    }

    config = {
        'max_num_arguments': 50
    }

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        """
        Count the number of dummy arguments and report if given
        maximum number exceeded.
        """
        num_arguments = len(subroutine.arguments)
        if num_arguments > config['max_num_arguments']:
            msg = (f'Subroutine has {num_arguments} dummy arguments '
                   f'(should not have more than {config["max_num_arguments"]})')
            rule_report.add(msg, subroutine)
