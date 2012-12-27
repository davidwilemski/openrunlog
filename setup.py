from setuptools import setup

setup(name='openrunlog',
      version='0.1',
      description='An open source web application to record and display your runs',
      url='http://github.com/davidwilemski/openrunlog',
      author='David Wilemski',
      author_email='david@davidwilemski.com',
      license='BSD',
      packages=['openrunlog'],
      install_requires=[
      ],
      test_suite='openrunlog.tests',
      zip_safe=False)
