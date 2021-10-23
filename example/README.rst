Example
=======

To run the example application, make sure you have the required
packages installed.  You can do this using following commands :

.. code-block:: bash

    mkvirtualenv example
    pip install -r example/requirements.txt

This assumes you already have ``virtualenv`` and ``virtualenvwrapper``
installed and configured.

Next, you can setup the django instance using :

.. code-block:: bash

    python example/manage.py migrate
    python example/manage.py loaddata example/initial_data.json

And run it :

.. code-block:: bash

    python example/manage.py runserver

Good luck!
