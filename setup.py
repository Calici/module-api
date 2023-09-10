from setuptools import \
    setup, \
    find_packages

setup(
    name='module-api',
    version='0.0.0',    
    description='A Python Package to communicate with the module frontend and backend',
    url='https://github.com/calici/module-api',
    author='Jonathan Willianto',
    author_email='jo.will@calici.co',
    license='MIT',
    packages=[ 
      *find_packages("module_api"), 
      *find_packages("common")
    ],
    install_requires=[
      "annotated-types==0.5.0",
      "certifi==2023.5.7",
      "charset-normalizer==3.1.0",
      "idna==3.4",
      "pydantic==2.0", 
      "pydantic_core==2.0.1",
      "pytz==2023.3",
      "PyYAML==6.0",
      "requests==2.31.0",
      "typing_extensions==4.7.1",
      "urllib3==2.0.3"
    ]
)