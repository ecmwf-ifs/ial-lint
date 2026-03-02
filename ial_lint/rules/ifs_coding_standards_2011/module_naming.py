# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from pathlib import Path

from loki.lint import GenericRule, RuleType


__all__ = ['ModuleNamingRule']


class ModuleNamingRule(GenericRule):  # Coding standards 1.5

    type = RuleType.WARN

    docs = {
        'id': '1.5',
        'title': ('Naming Schemes for Modules: All modules should end with "_mod". '
                  'Module filename should match the name of the module it contains.'),
    }

    @classmethod
    def check_module(cls, module, rule_report, config):
        '''Check the module name and the name of the source file.'''
        if not module.name.lower().endswith('_mod'):
            msg = f'Name of module "{module.name}" should end with "_mod"'
            rule_report.add(msg, module)

        if module.source.file:
            path = Path(module.source.file)
            if module.name.lower() != path.stem.lower():
                msg = f'Module filename "{path.name}" does not match module name "{module.name}"'
                rule_report.add(msg, module)
