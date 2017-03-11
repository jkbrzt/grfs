``grfs``
########

This app allows you to mount your `Ricoh GR II <http://amzn.to/1X0TwAH>`_
with FUSE over WiFi. It implements a read-only filesystem for accessing
photos on a Ricoh GR II camera over the built-in WiFi feature and the HTTP API
the camera exposes.


.. image:: https://raw.githubusercontent.com/jakubroztocil/grfs/master/grii.jpg



Why?
====

To be able to batch import photos from the camera to a computer wirelesly. 
For example, you might have a computer without an SD card reader
and without USB ports (looking at you, 2016 MacBook Pro) and ``grfs`` can be used as a work around.

This library was also created to experiment with the REST-ish API the Ricoh GR II
exposes for the 
`GR Remote <http://www.ricoh-imaging.co.jp/english/products/gr_remote/>`_ 
web-based app. 



Status
======

It works but it's really slow. Reasons for the slow speed being:

1. Slow WiFi by which the camera is equipped.
2. The necessity to make a ``GET`` request for each file individually to read the
   HTTP headers to determine file size.

When you mount the camera, you get three different folders ``thumb``, ``view``,
and ``full`` which correspond to the different image sizes available through
the camera's HTTP API. Note that ``view`` might no contain all the images
available.


Installation
============

1. Install FUSE on your system (e.g. ``brew install osxfuse``)
2. Install this package ``pip install grfs``


Usage
=====

1. Turn on your Ricoh GR II
2. Turn on the WiFi feature on the camera
3. Connect your computer to the WiFi network from the camera
4. Mount the camera ``grfs ~/GR`` (create the mountpoint directory first — ``mkdir ~/GR``)
5. Access your files ``ls -l ~/GR`` (or from you system file browser)



Contact
=======

Jakub Roztocil

* https://github.com/jakubroztocil
* https://twitter.com/jakubroztocil
* https://roztocil.co
