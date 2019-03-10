import pytest
from pycvs.cli import PyCvs

# Imports for mocking
import os.path
import shutil 
import sys
from colorama import Fore, Style

def get_class(mocker):
    init = mocker.patch.object(PyCvs, '__init__')
    init.return_value = None

    return PyCvs()

def test_no_tag_file(mocker):
    obj = get_class(mocker)
    mocker.patch.object(PyCvs, '_access_cvs', return_value=None)
    mocker.patch.object(os.path, 'isfile', return_value=False)
    pint = mocker.patch('builtins.print')

    obj._status()

    pint.assert_called_once_with('On branch HEAD')

def test_no_output(mocker):
    obj = get_class(mocker)
    ac_mock = mocker.patch.object(PyCvs, '_access_cvs')
    ac_mock.before = b"\n"
    mocker.patch.object(os.path, 'isfile', return_value=False)
    pint = mocker.patch('builtins.print')

    obj._status()

    pint.assert_has_calls([mocker.call('On branch HEAD'), mocker.call('nothing to commit, working directory clean')])

def test_locally_modified_crlf(mocker):
    obj = get_class(mocker)
    cvs_mock = mocker.MagicMock()
    cvs_mock.before = b"""
cvs server: Examining application/3rd_party/EMDG\r
===================================================================\r
File: EMDG.exe         	Status: Locally Modified\r

   Working revision:	1.3\r
   Repository revision:	1.3	/application/3rd_party/EMDG/EMDG.exe,v\r
   Sticky Tag:		pycvs_1_2_3 (revision: 1.3)\r
   Sticky Date:		(none)\r
   Sticky Options:	-kb\r\n"""
    mocker.patch.object(PyCvs, '_access_cvs', return_value=cvs_mock)
    mocker.patch.object(os.path, 'isfile', return_value=False)
    pint = mocker.patch('builtins.print')

    obj._status()

    pint.assert_has_calls([mocker.call('Changes staged for commit:'),
                           mocker.call(' (use cvs commit... to check them in)\n'),
                           mocker.call(Fore.GREEN, '\tmodified:\t', end=''),
                           mocker.call('application/3rd_party/EMDG/EMDG.exe         '),
                           mocker.call(Style.RESET_ALL, '')])

def test_had_conflicts_crlf(mocker):
    obj = get_class(mocker)
    cvs_mock = mocker.MagicMock()
    cvs_mock.before = b"""
cvs server: Examining application/3rd_party/EMDG\r
===================================================================\r
File: EMDG.exe         	Status: File had conflicts on merge\r

   Working revision:	1.3\r
   Repository revision:	1.3	/application/3rd_party/EMDG/EMDG.exe,v\r
   Sticky Tag:		pycvs_1_2_3 (revision: 1.3)\r
   Sticky Date:		(none)\r
   Sticky Options:	-kb\r\n"""
    mocker.patch.object(PyCvs, '_access_cvs', return_value=cvs_mock)
    mocker.patch.object(os.path, 'isfile', return_value=False)
    pint = mocker.patch('builtins.print')

    obj._status()

    pint.assert_has_calls([mocker.call('Files that had conflicts and need to be committed:'),
                           mocker.call(' (use cvs commit <file>... to check them in)\n'),
                           mocker.call(Fore.GREEN, '\tmerged:\t', end=''),
                           mocker.call('application/3rd_party/EMDG/EMDG.exe         '),
                           mocker.call(Style.RESET_ALL, '')])

def test_multiple_had_conflicts(mocker):
    obj = get_class(mocker)
    cvs_mock = mocker.MagicMock()
    cvs_mock.before = b"""
cvs server: Examining application/3rd_party/EMDG
===================================================================
File: EMDG.exe         	Status: File had conflicts on merge

   Working revision:	1.3
   Repository revision:	1.3	/application/3rd_party/EMDG/EMDG.exe,v
   Sticky Tag:		pycvs_1_2_3 (revision: 1.3)
   Sticky Date:		(none)
   Sticky Options:	-kb\n
cvs server: Examining application/2nd_party/ERP
===================================================================
File: rpxl.py         	Status: File had conflicts on merge

   Working revision:	1.5
   Repository revision:	1.5	/application/2nd_party/ERP/rpxl.py,v
   Sticky Tag:		pycvs_1_2_3 (revision: 1.5)
   Sticky Date:		(none)
   Sticky Options:	-kb\n"""
    mocker.patch.object(PyCvs, '_access_cvs', return_value=cvs_mock)
    mocker.patch.object(os.path, 'isfile', return_value=False)
    pint = mocker.patch('builtins.print')

    obj._status()

    pint.assert_has_calls([mocker.call('Files that had conflicts and need to be committed:'),
                           mocker.call(' (use cvs commit <file>... to check them in)\n'),
                           mocker.call(Fore.GREEN, '\tmerged:\t', end=''),
                           mocker.call('application/3rd_party/EMDG/EMDG.exe         '),
                           mocker.call(Fore.GREEN, '\tmerged:\t', end=''),
                           mocker.call('application/2nd_party/ERP/rpxl.py         '),
                           mocker.call(Style.RESET_ALL, '')])