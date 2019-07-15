from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='oauth_nk',
      version='0.1',
      description='The simple authentication ',
      url='https://github.com/pypa/sampleprojectoauth',
      author='NataliKV',
      author_email='NataliaKovalchuk37@gmail.com',
      license='MIT',
      packages=find_packages(),
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      )
