"""
   @copyright: 2010 - 2018 by Pauli Rikula <pauli.rikula@gmail.com>
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

from setuptools import setup
import category_equations


setup(
    name='python-category-equations',
    version='0.2.0',
    description='python-category-equations',
    long_description=category_equations.from_operator.__doc__,
    license="MIT",
    author="Pauli Rikula",
    url='https://github.com/kummahiih/python-category-equations',
    packages=['category_equations'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6']
)
    