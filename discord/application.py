"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Optional,
    Union,
    List
)

from .mixins import Hashable
from .enums import (
    ApplicationCommandType,
    ApplicationCommandOptionType,
    try_enum,
)


if TYPE_CHECKING:
    from .state import ConnectionState

    from .types.interactions import (
            ApplicationCommand as ApplicationCommandPayload,
            ApplicationCommandOption as ApplicationCommandOptionPayload,
            ApplicationCommandOptionChoice as ApplicationCommandOptionChoicePayload)

__all__ = (
    #Todo do we need all?
    'ApplicationCommandOptionChoice',
    'ApplicationCommandOption',
    'ApplicationCommand',
)


class ApplicationCommandOptionChoice(Hashable):
    """Represents a Discord application command option choice.

    .. versionadded:: 2.0

    .. container:: operations

        .. describe:: x == y

            Checks if two application command option choices are equal.

        .. describe:: x != y

            Checks if two application command option choices are not equal.

        .. describe:: hash(x)

            Returns the application command options choice's hash.

        .. describe:: str(x)

            Returns the application command options choics's name.

    Attributes
    ----------
    name: :class:`str`
        The name of the application command option choice.
    value: :class:`str`
        The value of the application command option choice.

    """

    __slots__ = (
        '_state',
        'name',
        'value'
    )

    def __init__(self, *, data: ApplicationCommandOptionChoicePayload, state: ConnectionState):
        self._state: ConnectionState = state
        self._from_data(data)

    def _from_data(self, applicationcommandoptionchoice: ApplicationCommandOptionChoicePayload) -> None:
        self.name: str = applicationcommandoptionchoice.get('name')
        self.value: Union[str, int] = applicationcommandoptionchoice.get('value')


class ApplicationCommandOption(Hashable):
    """Represents a Discord application command option.

    .. versionadded:: 2.0

    .. container:: operations

        .. describe:: x == y

            Checks if two application command options are equal.

        .. describe:: x != y

            Checks if two application command options are not equal.

        .. describe:: hash(x)

            Returns the application command options's hash.

        .. describe:: str(x)

            Returns the application command options's name.

    Attributes
    ----------
    name: :class:`str`
        The name of the application command option.
    description: :class:`str`
        The description of the application command.
    required: Optional[:class:`bool`]
        Shows whether the application command option is required.
    type: :class:`ApplicationCommandOptionType`
        The application commands option type (Whether it is a sub command, etc.)
    options: Optional[List[:class:`ApplicationCommandOptionType`]]
        The application command's options.
    choices: Optional[List[:class:`ApplicationCommandOptionChoice`]]
        The application command option choices.

    """

    __slots__ = (
        '_state',
        'type',
        'name',
        'description',
        'required',
        'choices',
        'options'
    )

    def __init__(self, *, data: ApplicationCommandOptionPayload, state:ConnectionState):
        self._state: ConnectionState = state
        self._from_data(data)

    def _from_data(self, applicationcommandoption: ApplicationCommandOptionPayload) -> None:
        self.type: ApplicationCommandOptionType = try_enum(ApplicationCommandOptionType,
                                                           applicationcommandoption.get('type'))
        self.name: str = applicationcommandoption.get('name')
        self.description: str = applicationcommandoption.get('description')
        self.required: Optional[bool] = applicationcommandoption.get('required')
        choices = applicationcommandoption.get('choices')
        self.choices: Optional[List[ApplicationCommandOptionChoice]] = [ApplicationCommandOptionChoice(state=self._state, data=choice) for choice in choices] if choices else None
        options = applicationcommandoption.get('options')
        self.options: Optional[List[ApplicationCommandOption]] = [ApplicationCommandOption(state=self._state, data=option) for option in options] if options else None


class ApplicationCommand(Hashable):
    """Represents a Discord application command.

    .. versionadded:: 2.0

    .. container:: operations

        .. describe:: x == y

            Checks if two application commands are equal.

        .. describe:: x != y

            Checks if two application commands are not equal.

        .. describe:: hash(x)

            Returns the application command's hash.

        .. describe:: str(x)

            Returns the application command's name.

    Attributes
    ----------
    id: :class:`int`
        The ID for the application command.
    name: :class:`str`
        The name of the application command.
    description: :class:`str`
        The description of the application command.
    guild_id: Optional[:class:`int`]
        The guild_id the application command belongs to, could be None when
        it is a guild command.
    type: :class:`AppicationCommandType`
        The application commands type (Whether it is a chat input command, etc.)
    options: Optional[List[:class:`ApplicationCommandOption`]]
        The application command's options.

    """

    __slots__ = (
        '_state',
        'id',
        'type',
        'application_id',
        'guild_id',
        'name',
        'description',
        'options'
    )

    def __init__(self, *, data: ApplicationCommandPayload, state:ConnectionState):
        self._state: ConnectionState = state
        self._from_data(data)

    def _from_data(self, applicationcommand: ApplicationCommandPayload) -> None:
        self.id: int = int(applicationcommand['id'])
        self.type: ApplicationCommandType = try_enum(ApplicationCommandType,
                                                      applicationcommand.get('type'))
        self.application_id: int = applicationcommand.get('application_id')
        self.guild_id: Optional[int] = applicationcommand.get('guild_id')
        self.name: str = applicationcommand.get('name')
        self.description: str = applicationcommand.get('description')
        options = applicationcommand.get('options')
        self.options: Optional[List[ApplicationCommandOption]] = [ApplicationCommandOption(state=self._state, data=option) for option in options] if options else None

    def __str__(self) -> str:
        return self.name

    async def delete(self) -> None:
        """|coro|

        Deletes the application command.

        Raises
        --------
        HTTPException
            Deleting the application command failed.
        """

        #Checks whether the application command has an guild_id attribute and deletes a guild command or a global command
        # depending on this
        if self.guild_id:
            return await self._state.http.delete_guild_command(self._state.self_id, self.guild_id, self.id)
        await self._state.http.delete_global_command(self._state.self_id, self.id)