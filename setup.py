"""
   @copyright: 2010 - 2018 by Pauli Rikula <pauli.rikula@gmail.com>
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

from setuptools import setup
import category_equations

README = category_equations.from_operator.__doc__

with open('README.md', 'wt') as readme_file:
    readme_file.write(README)

setup(
    name='python-category-equations',
    version='0.3.6',
    description='python-category-equations',
    long_description=README,
    license="MIT",
    author="Pauli Rikula",
    url='https://github.com/kummahiih/python-category-equations',
    packages=['category_equations'],
    python_requires='~=3.6',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6']
)
    