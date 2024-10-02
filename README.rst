RISC-V gadget
=============

Install dependencies
--------------------

.. code-block:: bash

    sudo apt-get install qemu-user-static
    sudo snap install ubuntu-image


Build image
-----------

.. code-block:: bash

    sudo ubuntu-image --debug classic image-definition.yaml

For debugging add --workdir /tmp/workdir.

First boot
----------

Login with user ubuntu, password ubuntu.
