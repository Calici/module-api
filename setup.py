from setuptools import setup

setup(
    name='module-api',
    version='0.0.0',    
    description='A Python Package to communicate with the module frontend and backend',
    url='https://github.com/calici/module-api',
    author='Jonathan Willianto',
    author_email='jo.will@calici.co',
    license='MIT',
    packages=[ 
      "module_api.API", 
      "module_api.common"
    ],
    install_requires=[
        "pyyaml", 
        "requests"
    ]
)