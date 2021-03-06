dis.py
==========

.. image:: https://discord.com/api/guilds/336642139381301249/embed.png
   :target: https://discord.gg/r3sSKJJ
   :alt: Discord server invite
.. image:: https://img.shields.io/pypi/v/discord.py.svg
   :target: https://pypi.python.org/pypi/dis.py
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/discord.py.svg
   :target: https://pypi.python.org/pypi/dis.py
   :alt: PyPI supported Python versions

A modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.

Why dis.py?
--------------------------

discord.py currently got disconnected due to multiple reasons. Read this `gist <https://gist.github.com/CuzImSyntax/4a2f62751b9600a31a0d3c78100287f1>`_ for more information.

dis.py is a fork of discord.py implementing discords new possibilities for devs such as application commands.

Key Features
-------------

- Modern Pythonic API using ``async`` and ``await``.
- Proper rate limit handling.
- Optimised in both speed and memory.

Installing
----------

**Python 3.8 or higher is required**

To install the library without full voice support, you can just run the following command:

Warning: This is currently still pointing to the old discord.py library and will be updated soon
You can install dis.py via git if you want to contribute or test the library.

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U discord.py

    # Windows
    py -3 -m pip install -U discord.py

Otherwise to get voice support you should run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "discord.py[voice]"

    # Windows
    py -3 -m pip install -U discord.py[voice]


To install the development version, do the following:

.. code:: sh

    $ git clone https://github.com/CuzImSyntax/dis.py
    $ cd dis.py
    $ python3 -m pip install -U .[voice]


Optional Packages
~~~~~~~~~~~~~~~~~~

* `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (for voice support)

Please note that on Linux installing voice you must install the following packages via your favourite package manager (e.g. ``apt``, ``dnf``, etc) before running the above commands:

* libffi-dev (or ``libffi-devel`` on some systems)
* python-dev (e.g. ``python3.6-dev`` for Python 3.6)

Quick Example
--------------

.. code:: py

    import discord

    class MyClient(discord.Client):
        async def on_ready(self):
            print('Logged on as', self.user)

        async def on_message(self, message):
            # don't respond to ourselves
            if message.author == self.user:
                return

            if message.content == 'ping':
                await message.channel.send('pong')

    client = MyClient()
    client.run('token')

Bot Example
~~~~~~~~~~~~~

.. code:: py

    import discord
    from discord.ext import commands

    bot = commands.Bot(command_prefix='>')

    @bot.command()
    async def ping(ctx):
        await ctx.send('pong')

    bot.run('token')

Slash Example
~~~~~~~~~~~~~

.. code:: py

    import discord
    from discord.ext import commands

    # We still need to set a prefix, as normal commands will also work.
    bot = commands.Bot(command_prefix='>')

    @bot.slash_command(description="Simple ping command.")
    async def ping(ctx):
        await ctx.reply('pong')

    bot.run('token')

You can find more examples in the examples directory.

Links
------
Warning: This is currently still pointing to the old discord.py links and will be updated soon

- `Documentation <https://dispy.readthedocs.io/en/latest/index.html>`_
-  Official Discord Server Not available
- `Discord API <https://discord.gg/discord-api>`_
