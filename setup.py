from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(name='dfcompare',
      version='0.1.1',
      packages=['dfcompare'],
      url='https://github.com/Yuhta/dfcompare',
      author="Jimmy Lu",
      author_email="gongchuo.lu@gmail.com",
      install_requires=['pandas'],
      long_description=long_description)
