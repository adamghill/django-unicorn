import toml

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys


# sys.path.insert(0, os.path.abspath("....django-unicorn"))


# -- Project information -----------------------------------------------------

project = "Unicorn"
copyright = "2023, Adam Hill"  # noqa: A001
author = "Adam Hill"

pyproject = toml.load("../../pyproject.toml")
version = pyproject["tool"]["poetry"]["version"]
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "rst2pdf.pdfbuilder",
    "autoapi.extension",
    "sphinxext.opengraph",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 3

myst_enable_extensions = ["colon_fence"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []
html_title = "Unicorn"

myst_heading_anchors = 3
myst_enable_extensions = ["linkify", "colon_fence"]

pdf_documents = [
    ("index", "unicorn-latest", "Unicorn", "Adam Hill"),
]

autoapi_dirs = [
    "../../django_unicorn",
]
autoapi_root = "api"
autoapi_add_toctree_entry = False
autoapi_generate_api_docs = True
# autoapi_keep_files = True  # useful for debugging generated errors
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
]
autoapi_type = "python"
autodoc_typehints = "signature"


def skip_member(app, what, name, obj, skip, options):  # noqa: ARG001
    if what == "data" and name.endswith(".logger"):
        skip = True
    elif "startunicorn" in name:
        skip = True

    return skip


def setup(sphinx):
    sphinx.connect("autoapi-skip-member", skip_member)


ogp_site_url = "https://www.django-unicorn.com/"
