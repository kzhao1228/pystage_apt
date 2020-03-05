============
 pyStage-APT
============

|LANGUAGE| |PY-VERSION| |PLATFORM_1| |PLATFORM_2| |SERIAL| |USB| |LICENSE|

``pystage-apt`` is a library to communicate with various Thorlabs’ APT single-channel controllers and control different types of Thorlabs’ actuator motors. It contains a large collection of motor control messages obtained from `Thorlabs APT Controllers Host-Controller Communications Protocol <https://github.com/kzhao1228/pystage_apt/blob/master/Doc/APT_Communications_Protocol_Rev_14.pdf>`__. This document describes the low-level communications protocol and commands used between the host PC and controller units within the APT family. Those messages are included in a series of python files and are stored in a folder named `ctrl_msg <https://github.com/kzhao1228/pystage_apt/tree/master/stage/ctrl_msg>`__.

In [1]:

.. code:: python

    from stage.motor_ini.core import find_stages
    s = list(find_stages())
    
Out [1]:

``Success: Stage MTS25-Z8 is detected and a controller with serial number 83845481 is connected via port /dev/ttyUSB1`` 

``Success: Stage Z812 is detected and a controller with serial number 83844171 is connected via port /dev/ttyUSB0``

In [2]:

.. code:: python
     
     s1 = s[1]
     s2 = s[0]
     
     s1.position
     s2.position
     
     s1.set_pos(3)
     s2.set_pos(2)
     
     s1.home_non_blocking()
     s2.home_non_blocking()
    
Out [2]:
     
``Homed``
     
The function ``find_stages`` `[1] <https://github.com/kzhao1228/pystage_apt/blob/master/stage/motor_ini/core.py>`__ scans all connected USB devices and searches for Thorlabs APT controllers. If no controllers is found, ``list(find_stages())`` returns an empty list. However, if one or more are found, ``list(find_stages())`` returns success messages along with a list of elements in *type* ``stage.motor_ctrl.MotorCtrl``. These elements store information as to controller serial number and created serial port entry in the arguments of *Classmethod* ``get_stages`` in *Class* ``SingleControllerPort`` `[2] <https://github.com/kzhao1228/pystage_apt/blob/master/stage/motor_ini/port.py>`__ respectively. This *Classmethod* returns information as to port entry, channel identity and stage model of the controllers, which are the required 
 
     
------------------------------------------

.. contents:: Table of contents
   :backlinks: top
   :local:


Installation
------------

Latest PyPI stable release
~~~~~~~~~~~~~~~~~~~~~~~~~~     

|PY-VERSION|

.. code:: sh

    pip install pystage-apt
    






.. |LICENSE| image:: https://img.shields.io/dub/l/vibe-d
   :target: https://raw.githubusercontent.com/kzhao1228/pystage_apt/master/LICENSE.txt
   :alt: License
   
.. |LANGUAGE| image:: https://img.shields.io/badge/python-v3.2%20|%20v3.3%20|%20v3.4%20|%20v3.5%20|%20v3.6%20|%20v3.7%20|%20v3.8-blue?&logo=python&logoColor=white
   :target: https://pypi.org/project/pystage-apt/
   :alt: Language

.. |PLATFORM_1| image:: https://img.shields.io/badge/platform-%20linux--64-blue?&logo=linux&logoColor=white
   :target: https://www.linux.org/pages/download/
   
.. |PLATFORM_2| image:: https://img.shields.io/badge/platform-%20raspbian-blue?&logo=Raspberry%20Pi
   :target: https://www.raspberrypi.org/downloads/raspbian/
   :alt: Platform_2   
   
.. |SERIAL| image:: https://img.shields.io/badge/pyserial-%20%3E=%202.7%20-important?&logo=koding&logoColor=white
   :target: https://github.com/pyserial/pyserial
   :alt: SERIAL
   
.. |USB| image:: https://img.shields.io/badge/pyusb-%20%3E=%201.0.0a%20-important?&logo=koding&logoColor=white
   :target: https://github.com/pyusb/pyusb
   :alt: USB
   
.. |PY-VERSION| image:: https://img.shields.io/badge/pypi-%20v0.0-blue?&logo=pypi&logoColor=white
   :target: https://pypi.org/project/pystage-apt/#history
   :alt: Py-version
