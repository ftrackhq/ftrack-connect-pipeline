..
    :copyright: Copyright (c) 2022 ftrack

.. _standalone:

**********
Standalone
**********

.. highlight:: bash

This section describes how to use the pipeline Framework in standalone mode, from with
the DCC application or outside.

***************
Python Example
***************

This is an example on how to run the framework in a python console without
Connect or any DCC running on the background, this way the framework is able to
discover any definition where the host type is python.

**mypipeline/standalone-snippets/python_standalone_publish_snippet.py**

.. literalinclude:: /resource/standalone-snippets/python_standalone_publish_snippet.py
    :language: python
    :linenos:


*****************
DCC Maya Example
*****************

This is an example on how to run the framework inside the maya console.
All the definitions with host_type maya and python will be discovered.


.. warning::

    Maya has to be launched using connect otherwise the user will have to
    manually setup all the environment variables for maya to be able to run the
    framework. We are working on providing an easy way to launch maya by command
    with the framework pre-loaded.

**mypipeline/standalone-snippets/maya_standalone_publish_snippet.py**

.. literalinclude:: /resource/standalone-snippets/maya_standalone_publish_snippet.py
    :language: python
    :linenos:
