# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

from loki import ir, flatten, as_tuple, Module, Subroutine
from loki.lint import GenericRule, RuleType
from loki.expression import symbols as sym


__all__ = ['DrHookRule']


class DrHookRule(GenericRule):  # Coding standards 1.9

    type = RuleType.SERIOUS

    docs = {
        'id': '1.9',
        'title': 'Rules for DR_HOOK',
    }

    non_exec_nodes = (ir.Comment, ir.CommentBlock, ir.Pragma, ir.PreprocessorDirective)

    @classmethod
    def _find_lhook_conditional(cls, ast, is_reversed=False):
        cond = None
        for node in reversed(ast) if is_reversed else ast:
            if isinstance(node, ir.Conditional):
                if node.condition == 'LHOOK':
                    cond = node
                    break
            elif not isinstance(node, cls.non_exec_nodes):
                # Break if executable statement encountered
                break
        return cond

    @classmethod
    def _find_lhook_call(cls, cond, is_reversed=False):
        call = None
        if cond:
            # We use as_tuple here because the conditional can be inline and then its body is not
            # iterable but a single node (e.g., CallStatement)
            body = reversed(as_tuple(cond.body)) if is_reversed else as_tuple(cond.body)
            for node in body:
                if isinstance(node, ir.CallStatement) and node.name == 'DR_HOOK':
                    call = node
                elif not isinstance(node, cls.non_exec_nodes):
                    # Break if executable statement encountered
                    break
        return call

    @staticmethod
    def _get_string_argument(scope):
        string_arg = scope.name.upper()
        while hasattr(scope, 'parent') and scope.parent:
            scope = scope.parent
            if isinstance(scope, Subroutine):
                string_arg = scope.name.upper() + '%' + string_arg
            elif isinstance(scope, Module):
                string_arg = scope.name.upper() + ':' + string_arg
        return string_arg

    @classmethod
    def _check_lhook_call(cls, call, subroutine, rule_report, pos='First'):
        if call is None:
            msg = f'{pos} executable statement must be call to DR_HOOK'
            rule_report.add(msg, subroutine)
        elif call.arguments:
            string_arg = cls._get_string_argument(subroutine)
            if not isinstance(call.arguments[0], sym.StringLiteral) or \
                    call.arguments[0].value.upper() != string_arg:
                msg = f'String argument to DR_HOOK call should be "{string_arg}"'
                rule_report.add(msg, call)
            second_arg = {'First': '0', 'Last': '1'}
            if not (len(call.arguments) > 1 and isinstance(call.arguments[1], sym.IntLiteral) and
                    str(call.arguments[1].value) == second_arg[pos]):
                msg = f'Second argument to DR_HOOK call should be "{second_arg[pos]}"'
                rule_report.add(msg, call)
            if not (len(call.arguments) > 2 and call.arguments[2] == 'ZHOOK_HANDLE'):
                msg = 'Third argument to DR_HOOK call should be "ZHOOK_HANDLE".'
                rule_report.add(msg, call)

    @classmethod
    def check_subroutine(cls, subroutine, rule_report, config, **kwargs):
        '''Check that first and last executable statements in the subroutine
        are conditionals with calls to DR_HOOK in their body and that the
        correct arguments are given to the call.'''
        # Extract the AST for the subroutine body
        ast = subroutine.body
        if isinstance(ast, ir.Section):
            ast = ast.body
        ast = flatten(ast)

        # Look for conditionals in subroutine body
        first_cond = cls._find_lhook_conditional(ast)
        last_cond = cls._find_lhook_conditional(ast, is_reversed=True)

        # Find calls to DR_HOOK
        first_call = cls._find_lhook_call(first_cond)
        last_call = cls._find_lhook_call(last_cond, is_reversed=True)

        cls._check_lhook_call(first_call, subroutine, rule_report)
        cls._check_lhook_call(last_call, subroutine, rule_report, pos='Last')
