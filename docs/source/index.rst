Favorite places
===============

A service for saving information about your favorite places.

Dependencies
============
Install the necessary software:

1. [Docker Desktop](https://www.docker.com).
2. [Git](https://github.com/git-guides/install-git).
3. [PyCharm](https://www.jetbrains.com/ru-ru/pycharm/download) (optional).


Installing
==========
Clone the repository:
    .. code-block::console
    git clone https://github.com/mnv/python-course-favorite-places.git

1. To configure the application, copy the contents of `.env.sample` to the `.env` file:
    .. code-block::console
    cp .env.sample .env

   This file contains environment variables whose values will be shared by the whole application.
   The sample file (`.env.sample`) contains a set of variables with default values,
   so it can be customized depending on the environment.

2. Build the container using Docker Compose:
    .. code-block::console
     docker compose build

    This command must be run from the root directory where `Dockerfile` is located.
    You also need to rebuild the docker container in case you have updated `requirements.txt`.

3. Configure the database for the application to work correctly.
   Apply migrations to create tables in the database:
    .. code-block::console
     docker compose run favorite-places-app alembic upgrade head

4. Now you can run the project inside the Docker container:
    .. code-block::console
    docker compose up

   When the containers are up, the server starts at [http://0.0.0.0:8010/docs](http://0.0.0.0:8010/docs).
   You can open it in your browser.


Using
=====



Database handling
------------------
To initialize the migration functionality, run the first run:
    .. code-block::console
    docker compose exec favorite-places-app alembic init -t async migrations

This command will create a directory with configuration files to configure the functionality of asynchronous migrations.

To create new migrations that will update the database tables to match the updated models,
run this command:
    .. code-block::console
    docker compose run favorite-places-app alembic revision --autogenerate -m "your description"

To apply the created migrations, perform the following steps:
    .. code-block::console
    docker compose run favorite-places-app alembic upgrade head


Automation
==========
The project contains a special `Makefile` which provides shortcuts to the command set:

1. Build the Docker container:
    .. code-block::console
    make build

2. Create Sphinx documentation:
    .. code-block::console
    make docs-html

3. autoformatting the source code:
    .. code-block::console
    make format

4. Static analysis (linters):
    .. code-block::console
    make lint

5. Autotests:
    .. code-block::console
    make test

    The test coverage report will be located at `src/htmlcov/index.html`.
    Thus, you can evaluate the quality of coverage of the automated tests.

6. Starting autoformat, linters and tests with one command:
    .. code-block::console
    make all

Run these commands from the source directory where `Makefile` is located.

Documentation
=============

Clients
=======
Basic
-----
.. automodule:: clients.base.base
    :members:

Geo-client
----------
.. automodule:: clients.geo
    :members:

Integrations
============
DB
--
.. automodule:: integrations.db.session
    :members:

Models
======
.. automodule:: models.mixins
    :members:
.. automodule:: models.places
    :members:

Repositories
============
.. automodule:: repositories.base_repository
    :members:
.. automodule:: repositories.places_repository
    :members:



Schematics
==========
.. automodule:: schemas.base
    :members:
.. automodule:: schemas.places
    :members:
.. automodule:: schemas.routes
    :members:

Services
========
.. automodule:: services.places_service
    :members:

Transportation
==============
.. automodule:: transport.handlers.places
    :members:

Translated with www.DeepL.com/Translator (free version)