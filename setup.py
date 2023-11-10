from setuptools import \
    setup, \
    find_packages, \
    find_namespace_packages

setup(
    name='module-api',
    version='0.0.10',    
    description='A Python Package to communicate with the module frontend and backend',
    url='https://github.com/calici/module-api',
    author='Jonathan Willianto',
    author_email='jo.will@calici.co',
    license='MIT',
    packages=[ 
      f"module_api.{pkg_name}" for pkg_name in find_namespace_packages("module_api")
    ],
    install_requires=[
      "annotated-types==0.5.0",
      "certifi==2023.7.22",
      "charset-normalizer==3.3.2",
      "idna==3.4",
      "pydantic==2.4.2", 
      "pydantic_core==2.10.1",
      "pytz==2023.3.post1",
      "PyYAML==6.0.1",
      "requests==2.31.0",
      "typing_extensions==4.7.1",
      "urllib3==2.0.7", 
      "pypharmaco @ https://github.com/Calici/pypharmaco/releases/download/v0.0.1/pypharmaco-0.0.1-py3-none-any.whl"
    ]
)