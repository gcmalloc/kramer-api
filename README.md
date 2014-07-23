A python implementation of parts of the kramer api destined to 
audio matrices. For example:

    import kramer
    device = kramer.Device()
    # this will link input 1 to output 9
    device.switch_audio(1, 9)
    # and this will link input 1 to output 10
    device.switch_audio(1, 10)

You can also specify a port and an ip for the Device

    device = kramer.Device()

#requirement
Tested with python2.7.

libraries (the setup.py will install them for you)

    * enum34 

# Installation
First clone the repo and go into it:

    git clone http://github.com/gcmalloc/kramer-api
    cd kramer-api

If you already have pip installed:

    pip install .

else you can do

    python setup.py install

This will install the library so you can use it.
