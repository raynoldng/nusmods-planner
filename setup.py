from setuptools import setup, find_packages

setup(name='nusmodsplanner',
      version='0.3',
      url='https://github.com/raynoldng/nusmods-planner',
      license='MIT',
      author='Bay Wei Heng, Raynold Ng',
      author_email='raynold.ng24@gmail.com',
      description='Constrain based timetable planner for NUS',
      packages=find_packages(exclude=['tests']),
      long_description=open('README.md').read(),
      zip_safe=False,
      setup_requires=['nose>=1.0'],
      test_suite='nose.collector')
