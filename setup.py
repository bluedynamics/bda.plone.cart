import os
from setuptools import setup
from setuptools import find_packages


version = "2.0.dev0"
shortdesc = "Shopping Cart"
longdesc = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()
longdesc += open(os.path.join(os.path.dirname(__file__), "CHANGES.rst")).read()
longdesc += open(os.path.join(os.path.dirname(__file__), "LICENSE.rst")).read()


setup(
    name="bda.plone.cart",
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
    author="BlueDynamics Alliance",
    author_email="dev@bluedynamics.com",
    license="GNU General Public Licence",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["bda", "bda.plone"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "bda.plone.ajax",
        "Products.CMFPlone",
        "setuptools",
        "simplejson>=3.12",
        "plone.restapi>=6.13.7",
        "zope.deferredimport",
        "zope.deprecation",
    ],
    extras_require={"test": ["plone.app.testing", "mock"]},
)
