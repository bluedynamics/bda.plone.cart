from setuptools import setup, find_packages
import os

version = '1.0dev'
shortdesc = "Shopping Cart"
longdesc = (
            open(os.path.join(os.path.dirname(__file__), 'README.rst')).read() 
            + '\n' +
            open('CHANGES.txt').read()
            + '\n')

setup(name='bda.plone.cart',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Environment :: Web Environment',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      license='GNU General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['bda', 'bda.plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'simplejson',
          'Plone',
          'bda.plone.ajax',
          'bda.plone.shipping',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)