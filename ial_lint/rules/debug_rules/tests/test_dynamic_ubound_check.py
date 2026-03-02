# (C) Copyright 2018- ECMWF.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import os
import importlib
from pathlib import Path
import pytest

from loki import Sourcefile, FindInlineCalls, FindNodes, VariableDeclaration
from loki.lint import DefaultHandler

from conftest import run_linter


@pytest.fixture(scope='module', name='rules')
def fixture_rules():
    rules = importlib.import_module('ial_lint.rules.debug_rules')
    return rules


def test_dynamic_ubound_checks(rules):
    """
    Test the run-time UBOUND checking linter rule
    """

    fcode = """
subroutine kernel(klon, klev, nblk, var0, var1, var2, var3, var4)
use abort_mod
implicit none
integer, intent(in) :: klon, klev, nblk
real, dimension(:,:,:), intent(inout) :: var0, var1
real, dimension(:,:,:), intent(inout) :: var2
real, intent(inout) :: var3(:,:), var4(:,:,:)

if(ubound(var0, 1) < klon)then
  call abort('kernel: first dimension of var0 too short')
endif
if(ubound(VAR0, 2) < klev)then
  call abort('kernel: second dimension of var0 too short')
endif
if(nblk > UBoUND(vAr0, 3))then
  call abort('kernel: third dimension of var0 too short')
endif

if(nblk > UBOUND(var1, 3))then
  call abort('kernel: third dimension of var1 too short')
endif

if(ubound(var2, 1) < klon .and. ubound(var2, 2) < klev .and. ubound(var2, 3) < nblk)then
  call abort('kernel: dimensions of var2 too short')
endif

if(ubound(var4, 1) < klon .and. ubound(var4, 2) < klev .and. ubound(var4, 3) < nblk)then
  call abort('kernel: dimensions of var4 too short')
endif

call some_other_kernel(klon, klen, nblk, var0, var1, var2, var3, var4)

end subroutine kernel
    """.strip()

    kernel = Sourcefile.from_source(fcode)
    kernel.path = Path(__file__).parent / 'dynamic_ubound_test.F90'

    messages = []
    handler = DefaultHandler(target=messages.append)
    _ = run_linter(kernel, [rules.DynamicUboundCheckRule], config={'fix': True}, handlers=[handler])

    # check rule violations
    assert len(messages) == 3
    assert all('DynamicUboundCheckRule' in msg for msg in messages)

    assert 'var0' in messages[0]
    assert 'var2' in messages[1]
    assert 'var4' in messages[2]

    # check fixed subroutine
    routine = kernel['kernel']
    icalls = [call for call in FindInlineCalls(unique=False).visit(routine.body)
              if call.function == 'ubound']

    assert len(icalls) == 1

    shape = ('klon', 'klev', 'nblk')

    assert all(s.name == d for s, d in zip(routine.variable_map['var0'].shape, shape))
    assert all(s.name == d for s, d in zip(routine.variable_map['var2'].shape, shape))
    assert all(s.name == d for s, d in zip(routine.variable_map['var4'].shape, shape))

    arg_names = ['klon', 'klev', 'nblk', 'var0', 'var1', 'var2', 'var3', 'var4']
    assert [arg.name.lower() for arg in routine.arguments] == arg_names

    # check that variable declarations have not been duplicated
    declarations = FindNodes(VariableDeclaration).visit(routine.spec)
    symbols = [s.name.lower() for decl in declarations for s in decl.symbols]
    assert len(symbols) == 8
    assert set(symbols) == {'klon', 'klev', 'nblk', 'var0', 'var1', 'var2', 'var3', 'var4'}

    # check number of declarations and symbols per declarations
    assert len(declarations) == 5
    assert len(declarations[0].symbols) == 3
    for decl in declarations[1:4]:
        assert len(decl.symbols) == 1
    assert len(declarations[4].symbols) == 2

    os.remove(kernel.path)
