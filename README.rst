============
 pyStage-APT
============

|LANGUAGE| |PY-VERSION| |GITHUB-TAG| |PLATFORM_I| |PLATFORM_II| |SERIAL| |USB| |LICENSE| |COUNTS-TOT| |COUNTS-TOD| 

``pystage-apt`` is a library to communicate with various Thorlabs’ APT single-channel controllers and control different types of Thorlabs’ actuator motors. It contains a large collection of motor control messages obtained from `Thorlabs APT Controllers Host-Controller Communications Protocol <https://https://github.com/kzhao1228/pystage_apt/blob/master/doc/APT_Communications_Protocol_Rev_15.pdf>`__. This document describes the low-level communications protocol and commands used between the host PC and controller units within the APT family. Those messages are included in a series of python files and are stored in a folder named `ctrl_msg <https://github.com/kzhao1228/pystage_apt/tree/master/stage/ctrl_msg>`__.

After you connect Thorlabs APT controllers (with stages connected) to your PC or a Raspberry Pi through USB ports, type and run the code below in, for example, Terminal, to get the controllers discovered by ``pystage-apt``. 

>>> from stage.motor_ini.core import find_stages
>>> s = list(find_stages())
Success: Stage MTS25-Z8 is detected and a controller with serial number 83845481 is connected via 
port /dev/ttyUSB1
Success: Stage Z812 is detected and a controller with serial number 83844171 is connected via 
port /dev/ttyUSB0

Once you see the success messages like these, congratulations, the controllers along with the stages are 'constructed' and are ready to be manipulated through recognised commands! Ta-da!

>>> s1 = s[1]
>>> s2 = s[0]
>>> s1.status
>>> s2.status

``pystage-apt`` works on Linux and Raspbian, in any console or in a GUI, and is also friendly with IPython/Jupyter notebooks. 
     
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
    
    
Latest development release on GitHub
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

|GITHUB-TAG|

Pull and install in the current directory:

.. code:: sh

    pip install -e git+https://github.com/kzhao1228/pystage_apt.git@master#egg=pystage_apt
    
Changelog
---------

The list of all changes is available on GitHub's Releases: |GITHUB-TAG|
    
Platform
--------

|PLATFORM_I| |PLATFORM_II|

``pystage-apt`` supports computationally constructing Thorlabs APT controllers on Linux and Raspbian. It may work on MacOS too only if you can find a way to create a ``/dev`` entry for raw access to USB devices. Because currently there is no way to access them as ``tty`` devices. For Windows, you can try `thorlabs_apt <https://github.com/qpit/thorlabs_apt>`__.

Note that, before you try to implement this library, you should first configure the ``/etc/udev/rules.d/99-com.rules`` file to avoid potential access permission error on USB device. To do this, open a Terminal window, type and run the command:

.. code:: sh

     sudo nano /etc/udev/rules.d/99-com.rules

Adding to this file with contents like this:

.. code:: sh

     SUBSYSTEM=="usb", ATTR{idVendor}=="HEX1", ATTR{idProduct}=="HEX2", MODE="0666"

where **HEX1** and **HEX2** are replaced with the vendor and product id respectively. For example, this content could be:

.. code:: sh

     SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="faf0", MODE="0666"
     
However, if you don't know the information, you could try typing and running the command ``lsusb`` in Terminal which should give you:

.. code:: sh

     Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
     Bus 001 Device 004: ID 0403:faf0 Future Technology Devices International, Ltd 
     Bus 001 Device 003: ID 0403:faf0 Future Technology Devices International, Ltd 
     Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
     Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

where ``idVendor:idProduct`` contains the information you need. After finishing editing the file, hit ``Ctrl+O`` to write out and hit ``enter`` to confirm the file name. To exit the file editing mode, simply hit ``Ctrl+X``.


Algorithm
---------

Function ``find_stages`` `[1] <https://github.com/kzhao1228/pystage_apt/blob/310c53fc141731c91ac55acff9fb34c7695f31c1/stage/motor_ini/core.py#L8>`__ scans all connected USB devices and searches for Thorlabs APT controllers. If no controllers are found, function ``list(find_stages())`` returns an empty list. However, if one or more are found, ``list(find_stages())`` returns success messages along with a list of elements in *type* ``stage.motor_ctrl.MotorCtrl``. These elements, which read ``SingleControllerPort('PORT_ENTRY',SERIAL_NO)``, store information as to created serial port entry and controller serial number in the arguments of *Class* ``SingleControllerPort`` `[2] <https://github.com/kzhao1228/pystage_apt/blob/a9579e028c0e7241116439e2998256e0b1a91166/stage/motor_ini/port.py#L202>`__ respectively. This *class* contains a *method* named ``get_stages`` that calls *class* ``MotorCtrl`` `[3] <https://github.com/kzhao1228/pystage_apt/blob/310c53fc141731c91ac55acff9fb34c7695f31c1/stage/motor_ctrl/__init__.py#L9>`__, stores it in a dictionary as a value of a key and returns the dictionary. This value is extracted by functions ``p = Port.create('PORT_ENTRY',SERIAL_NO)`` and ``p.get_stages().values()`` `[4] <https://github.com/kzhao1228/pystage_apt/blob/a9579e028c0e7241116439e2998256e0b1a91166/stage/motor_ini/core.py#L45>`__ when ``find_stages`` `[1] <https://github.com/kzhao1228/pystage_apt/blob/310c53fc141731c91ac55acff9fb34c7695f31c1/stage/motor_ini/core.py#L8>`__ is being implemented.

``Port.create('PORT_ENTRY',SERIAL_NO)`` `[4] <https://github.com/kzhao1228/pystage_apt/blob/a9579e028c0e7241116439e2998256e0b1a91166/stage/motor_ini/core.py#L45>`__ calls *method* ``create`` `[5] <https://github.com/kzhao1228/pystage_apt/blob/a9579e028c0e7241116439e2998256e0b1a91166/stage/motor_ini/port.py#L183>`__ of *class* ``Port`` `[6] <https://github.com/kzhao1228/pystage_apt/blob/a9579e028c0e7241116439e2998256e0b1a91166/stage/motor_ini/port.py#L10>`__ which then calls ``SingleControllerPort`` `[2] <https://github.com/kzhao1228/pystage_apt/blob/a9579e028c0e7241116439e2998256e0b1a91166/stage/motor_ini/port.py#L202>`__ and returns it. Therefore, ``list(find_stages())`` basically returns a list of callable ``MotorCtrl`` `[3] <https://github.com/kzhao1228/pystage_apt/blob/310c53fc141731c91ac55acff9fb34c7695f31c1/stage/motor_ctrl/__init__.py#L9>`__, each of which is dependent of a detected stage. Upon calling *instances*, *properties* and *methods* included in ``MotorCtrl`` `[3] <https://github.com/kzhao1228/pystage_apt/blob/310c53fc141731c91ac55acff9fb34c7695f31c1/stage/motor_ctrl/__init__.py#L9>`__, their corresponding control messages `[5] <https://github.com/kzhao1228/pystage_apt/tree/master/stage/ctrl_msg>`__ are invoked to structure a series of instructions to be delivered to the controllers and these instructions are decoded to strings of hexadecimal characters that can be understood by the controllers before they are sent out.

 
 
LICENSE
-------

Open Source (OSI approved): |LICENSE|




.. |LICENSE| image:: https://img.shields.io/dub/l/vibe-d
   :target: https://raw.githubusercontent.com/kzhao1228/pystage_apt/master/LICENSE.txt
   :alt: License
   
.. |LANGUAGE| image:: https://img.shields.io/badge/python-v3.2%20|%20v3.3%20|%20v3.4%20|%20v3.5%20|%20v3.6%20|%20v3.7%20|%20v3.8-blue?&logo=python&logoColor=white
   :target: https://pypi.org/project/pystage-apt/
   :alt: Language

.. |PLATFORM_I| image:: https://img.shields.io/badge/platform-linux--64-blue?&logo=linux&logoColor=white
   :target: https://www.linux.org/pages/download/
   :alt: Platform_i
   
.. |PLATFORM_II| image:: https://img.shields.io/badge/platform-raspbian-blue?&logo=Raspberry%20Pi
   :target: https://www.raspberrypi.org/downloads/raspbian/
   :alt: Platform_ii
   
.. |SERIAL| image:: https://img.shields.io/badge/pyserial-%3E=2.7-important?&logo=koding&logoColor=white
   :target: https://github.com/pyserial/pyserial
   :alt: SERIAL
   
.. |USB| image:: https://img.shields.io/badge/pyusb-%3E=1.0.0a-important?&logo=koding&logoColor=white
   :target: https://github.com/pyusb/pyusb
   :alt: USB
   
.. |PY-VERSION| image:: https://img.shields.io/badge/pypi-v0.2-blue?&logo=pypi&logoColor=white
   :target: https://pypi.org/project/pystage-apt/#history
   :alt: Py-version
  
.. |GITHUB-TAG| image:: https://img.shields.io/badge/tag-%20%20v0.2-blue?&logo=github
   :target: https://github.com/kzhao1228/pystage_apt/releases
   :alt: GitHub-tags
   
.. |COUNTS-TOT| image:: https://visitor-badge.glitch.me/badge?page_id=kzhao1228.pystage-apt
   :target: https://github.com/kzhao1228/pystage_apt/blob/master/README.rst
   :alt: Counts-total
   
.. |COUNTS-TOD| image:: https://visitor-badge.glitch.me/badge?page_id=kzhao1228.pystage-apt   
   :target: https://github.com/kzhao1228/pystage_apt/blob/master/README.rst
   :alt: Counts-today
