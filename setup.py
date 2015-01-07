from setuptools import setup

setup(
    name =          'InvInc',
    version =       '0.2.0-dev',
    url =           'https://github.com/brandjon/oinc/oinc',
    
    author =        'Jon Brandvein',
    author_email =  'jon.brandvein@gmail.com',
#    license =       ...,
    description =   'A system for compiling queries into ' \
                    'incremental demand-driven code',
    
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Compilers',
    ],
    
    packages =      ['oinc'],
    
    test_suite =    'oinc.tests',
    
    install_requires = [
        'simplestruct >=0.2.1',
        'iast >=0.2.1',
    ],
)
