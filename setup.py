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

setup(name = 'PyStage-APT',
      version = '0.0.0',
      url = 'https://github.com/kzhao1228/pystage_apt',
      license = 'MIT',
      author = 'Kaixiang Zhao',
      author_email = 'kz1619@ic.ac.uk',
      description = 'A Python library for Thorlabs\' APT stage controllers',
      long_description = 'pystage_apt is a python library to control various Thorlabs\' APT stage controllers with single channel',
      platforms = '[Linux]',
      packages = PACKAGES,
      install_requires = ['pyusb>=1.0.0a','pyserial>=2.7'],
      classifiers = CLASSIFIERS,
      python_requires = '>=3',
      data_files = [('',['LICENSE.txt'])],
      zip_safe = False
)
      
      