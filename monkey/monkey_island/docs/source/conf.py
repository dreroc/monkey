# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../../../"))
sys.path.insert(0, os.path.abspath("../../../monkey/"))
sys.path.insert(0, os.path.abspath("../../../monkey/common"))
sys.path.insert(0, os.path.abspath("../../../monkey/infection_monkey/"))
sys.path.insert(0, os.path.abspath("../../../monkey/monkey_island/"))


# -- Project information -----------------------------------------------------

project = "Infection Monkey"
copyright = "2022, Akamai Ltd"
author = "Akamai Ltd"

# The short X.Y version
version = ""
# The full version, including alpha/beta/rc tags
release = "0.0.0"


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",  # automatic documentation of single docstring
    "sphinx.ext.autosummary",  # using autodoc automatic documentation of whole modules
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",  # references to external documentation
    "sphinx.ext.extlinks",
    "sphinx_rtd_theme",  # ReadTheDocs theme
    "sphinx.ext.inheritance_diagram",  # used for showing the inheritence diagram
]
autosummary_generate = True
autosummary_imported_members = False
autodoc_member_order = "groupwise"

autodoc_mock_imports = [
    #    "flask",
    #    "netifaces",
    #    `"psutil",
    #    "flask_restful",
    #    "impacket",
    #    "paramiko",
    #    "gridfs",
    #    "flask_pymongo",
    #    "pypsrp",
    "pymongo",
    #    "ring",
    #    "botocore",
    #    "flask_jwt_extended",
    #    "pypykatz",
    #    "spnego",
    #    "jwt",
    #    "bcrypt",
    #    "Crypto",
    #    "twisted",
    #    "pymssql",
    #    "nmb",
    #    "odict",
    #    "pyAesCrypt",
    #    "dpath",
    "gevent",
    "ntsecuritycon",
    #    "bson",
    "win32api",
    #    "werkzeug",
    #    "jsonschema",
    #    "boto3",
    #    "dateutil",
    "win32con",
    "win32security",
]

# Mappings for sphinx.ext.intersphinx. Projects have to have Sphinx-generated doc! (.inv file)
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

autoclass_content = "both"  # Add __init__ doc (ie. params) to class summaries
html_show_sourcelink = False  # Remove 'view source code' from top of page (for html, not python)
autodoc_inherit_docstrings = True  # If no docstring, inherit from base class
set_type_checking_flag = True  # Enable 'expensive' imports for sphinx_autodoc_typehints
autodoc_typehints = "both"  # Sphinx-native. Not as good as sphinx_autodoc_typehints
add_module_names = False  # Remove namespaces from class/method signatures
html_show_sphinx = False  # Shows "Build with Sphinx and RTD schem text at footer"
html_show_copyright = True  # Shows copyright using the company and author specified above

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["*node_modules*"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_favicon = "_static/images/favicon.ico"
html_logo = "_static/images/logo.gif"
# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {"logo_only": "true"}

# "Edit on Github" button
html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "guardicore",  # Username
    "github_repo": "monkey",  # Repo name
    "github_version": "develop",  # Version
    "conf_py_path": "/monkey/monkey_island/docs/source/",  # Path in the checkout to the docs root
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}

# Adding CSS files to make it more like the Hugo documentation

html_css_files = [
    "css/all.css",
    "css/all.min.css",
    "css/bootstrap-grid.min.css",
    "css/bootsrap-grid.min.css.map",
    "css/brands.css",
    "css/brands.min.css",
    "css/fontawesome.css",
    "css/fontawesome.min.css",
    "css/labels.css",
    "css/regular.css",
    "css/regular.min.css",
    "css/shadow_around_images.css",
    "css/solid.css",
    "css/solid.min.css",
    "css/svg-with-js.css",
    "css/svg-with-js.min.css",
    "css/v4-shims.css",
    "css/v4-shims.min.css",
    "css/custom.css",
]

# TODO: Investigate if we really need them,
# html_js_files = ["js/bootstrap.min.js", "js/bootstrap.min.js.map"]

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "InfectionMonkeydoc"


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "InfectionMonkey.tex", "Infection Monkey Documentation", "Akamai Ltd", "manual"),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "infectionmonkey", "Infection Monkey Documentation", [author], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "InfectionMonkey",
        "Infection Monkey Documentation",
        author,
        "InfectionMonkey",
        "One line description of project.",
        "Miscellaneous",
    ),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ["search.html"]


# -- Extension configuration -------------------------------------------------
