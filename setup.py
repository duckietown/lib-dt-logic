from setuptools import find_packages, setup

# :==> Fill in your project data here
# The package name is the name on PyPI
# it is not the python module names.
package_name = "dt-logic"
library_webpage = f"http://github.com/duckietown/lib-{package_name}"
maintainer = "Shengjie Hu"
maintainer_email = "shengjie@duckietown.org"
short_description = "High level logic operations for Duckietown's autonomy behavior."
full_description = """
To switch the modes of the robots in Duckietown among scenarios, e.g. autonomous, manual, multi-agent.
Primarily, a finite state machine tool with actions callbacks based on state transitions, and visualization.
"""

# Read version from the __init__ file
def get_version_from_source(filename):
    import ast

    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith("__version__"):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError("No version found in %r." % filename)
    if version is None:
        raise ValueError(filename)
    return version


version = get_version_from_source(f"src/{package_name.replace('-', '_')}/__init__.py")

install_requires = [
    "networkx<=2.7.1",
    "matplotlib<=3.5.1",
]
tests_require = []

# compile description
underline = "=" * (len(package_name) + len(short_description) + 2)
description = """
{name}: {short}
{underline}

{long}
""".format(
    name=package_name,
    short=short_description,
    long=full_description,
    underline=underline,
)

packages = find_packages("./src")

print("The following packages were found:\n\t - " + "\n\t - ".join(packages) + "\n")

# setup package
setup(
    name=f"lib-{package_name}",
    author=maintainer,
    author_email=maintainer_email,
    url=library_webpage,
    tests_require=tests_require,
    install_requires=install_requires,
    package_dir={"": "src"},
    packages=find_packages("./src"),
    long_description=description,
    version=version,
)
