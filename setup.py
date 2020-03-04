from setuptools import setup, find_packages


CLASSIFIERS = [
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development :: Libraries',
    'Topic :: System :: Hardware',
    'Operating System :: POSIX :: Linux'
        
]

PACKAGES = [
    'stage',
    'stage/motor_ini',
    'stage/motor_ctrl',
    'stage/ctrl_msg'
]

LONG_DESCRIPTION = 'pystage-apt is a library to communicate with various Thorlabs\' APT single-channel controllers ' +\
    'and control different types of Thorlabs\' actuator motors. ' +\
    'It contains a large collection of motor control messages obtained from Thorlabs APT Controllers ' +\
    'Host-Controller Communications Protocol. This document describes the low-level communications ' +\
    'protocol and commands used between the host PC and controller units within the APT family. ' +\
    'Those messages are included in a series of python files and are stored in a folder named ctrl_msg. '
    

setup(name = 'pystage_apt',
      version = '0.0',
      url = 'https://github.com/kzhao1228/pystage_apt',
      license = 'MIT',
      author = 'Kaixiang Zhao',
      author_email = 'kz1619@ic.ac.uk',
      description = 'A python library for Thorlabs\' APT single-channel controllers',
      long_description = LONG_DESCRIPTION,
      platforms = ['Linux'],
      packages = PACKAGES,
      install_requires = ['pyusb>=1.0.0a','pyserial>=2.7'],
      classifiers = CLASSIFIERS,
      python_requires = '>=3',
      data_files = [('',['LICENSE.txt'])],
      zip_safe = False
)
      
      