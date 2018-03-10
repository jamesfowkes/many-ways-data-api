from setuptools import setup

setup(
    name='Many Data',
    version='0.1',
    long_description=__doc__,
    packages=['many_ways'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask',
                      'Flask-Restful']
)
