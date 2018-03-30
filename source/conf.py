#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Cloud-Player API documentation build configuration file
#

import os.path as path
import sys
import mock
import setuptools
from recommonmark.parser import CommonMarkParser

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
with mock.patch.object(setuptools, 'setup') as mock_setup:
    import setup as _setup  # NOQA
package_info = mock_setup.call_args[1]


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode']

source_parsers = {'.md': CommonMarkParser}
source_suffix = ['.rst', '.md']
master_doc = 'index'

project = package_info['name']
copyright = package_info['license']
author = package_info['author']
version = package_info['version']
release = version.replace('.dev0', '')

exclude_patterns = []
pygments_style = 'sphinx'
todo_include_todos = True
htmlhelp_basename = 'Cloud-PlayerAPIdoc'
html_theme = 'alabaster'
html_theme_options = {
    'show_related': True
}
html_static_path = ['../static']
html_sidebars = {
    '**': [
        'relations.html',
        'searchbox.html',
    ]
}
