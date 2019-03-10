import pytest
from pycvs.cli import PyCvs

# Imports for mocking
import os.path
import shutil 
import sys

def get_class(mocker):
    init = mocker.patch.object(PyCvs, '__init__')
    init.return_value = None

    return PyCvs()

def test_no_parameter(mocker):
    obj = get_class(mocker)
    mocker.patch.object(sys, 'argv', ['pycvs'])
    pint = mocker.patch('builtins.print')

    obj.process()

    pint.assert_called_once_with("Nothing to do")

def test_checkout_no_parameter(mocker):
    obj = get_class(mocker)
    mocker.patch.object(sys, 'argv', ['pycvs', 'checkout'])
    pint = mocker.patch('builtins.print')

    obj.process()

    pint.assert_called_once_with("Missing arguments for checkout command")

def test_co_no_parameter(mocker):
    obj = get_class(mocker)
    mocker.patch.object(sys, 'argv', ['pycvs', 'co'])
    pint = mocker.patch('builtins.print')

    obj.process()

    pint.assert_called_once_with("Missing arguments for co command")

def test_checkout_parameters(mocker):
    obj = get_class(mocker)
    mocker.patch.object(sys, 'argv', ['pycvs', 'co', 'module/', 'to', 'test'])
    check = mocker.patch.object(PyCvs, '_checkout')

    obj.process()

    check.assert_called_once_with(['module/', 'to', 'test'])