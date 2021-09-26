"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz 2021-present CuzImSyntax

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

import inspect
import re

from typing import Any, Dict, Generic, List, Optional, TYPE_CHECKING, TypeVar, Union

import discord.abc
import discord.utils

from discord.message import Message
from discord.interactions import Interaction

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    from discord.abc import MessageableChannel
    from discord.guild import Guild
    from discord.member import Member
    from discord.state import ConnectionState
    from discord.user import ClientUser, User
    from discord.voice_client import VoiceProtocol

    from .bot import Bot, AutoShardedBot
    from .cog import Cog
    from .core import Command, AppCommand
    from .help import HelpCommand
    from .view import StringView
    from discord.utils import copy_doc

__all__ = (
    'Context',
    'InteractionContext'
)

MISSING: Any = discord.utils.MISSING

T = TypeVar('T')
BotT = TypeVar('BotT', bound="Union[Bot, AutoShardedBot]")
CogT = TypeVar('CogT', bound="Cog")

if TYPE_CHECKING:
    P = ParamSpec('P')
else:
    P = TypeVar('P')


class Context(discord.abc.Messageable, Generic[BotT]):
    r"""Represents the context in which a command is being invoked under.

    This class contains a lot of meta data to help you understand more about
    the invocation context. This class is not created manually and is instead
    passed around to commands as the first parameter.

    This class implements the :class:`~discord.abc.Messageable` ABC.

    Attributes
    -----------
    message: :class:`.Message`
        The message that triggered the command being executed.
    bot: :class:`.Bot`
        The bot that contains the command being executed.
    args: :class:`list`
        The list of transformed arguments that were passed into the command.
        If this is accessed during the :func:`.on_command_error` event
        then this list could be incomplete.
    kwargs: :class:`dict`
        A dictionary of transformed arguments that were passed into the command.
        Similar to :attr:`args`\, if this is accessed in the
        :func:`.on_command_error` event then this dict could be incomplete.
    current_parameter: Optional[:class:`inspect.Parameter`]
        The parameter that is currently being inspected and converted.
        This is only of use for within converters.

        .. versionadded:: 2.0
    prefix: Optional[:class:`str`]
        The prefix that was used to invoke the command.
    command: Optional[:class:`Command`]
        The command that is being invoked currently.
    invoked_with: Optional[:class:`str`]
        The command name that triggered this invocation. Useful for finding out
        which alias called the command.
    invoked_parents: List[:class:`str`]
        The command names of the parents that triggered this invocation. Useful for
        finding out which aliases called the command.

        For example in commands ``?a b c test``, the invoked parents are ``['a', 'b', 'c']``.

        .. versionadded:: 1.7

    invoked_subcommand: Optional[:class:`Command`]
        The subcommand that was invoked.
        If no valid subcommand was invoked then this is equal to ``None``.
    subcommand_passed: Optional[:class:`str`]
        The string that was attempted to call a subcommand. This does not have
        to point to a valid registered subcommand and could just point to a
        nonsense string. If nothing was passed to attempt a call to a
        subcommand then this is set to ``None``.
    command_failed: :class:`bool`
        A boolean that indicates if the command failed to be parsed, checked,
        or invoked.
    """

    def __init__(self,
                 *,
                 message: Message,
                 bot: BotT,
                 view: StringView,
                 args: List[Any] = MISSING,
                 kwargs: Dict[str, Any] = MISSING,
                 prefix: Optional[str] = None,
                 command: Optional[Command] = None,
                 invoked_with: Optional[str] = None,
                 invoked_parents: List[str] = MISSING,
                 invoked_subcommand: Optional[Command] = None,
                 subcommand_passed: Optional[str] = None,
                 command_failed: bool = False,
                 current_parameter: Optional[inspect.Parameter] = None,
                 ):
        self.message: Message = message
        self.bot: BotT = bot
        self.args: List[Any] = args or []
        self.kwargs: Dict[str, Any] = kwargs or {}
        self.prefix: Optional[str] = prefix
        self.command: Optional[Command] = command
        self.view: StringView = view
        self.invoked_with: Optional[str] = invoked_with
        self.invoked_parents: List[str] = invoked_parents or []
        self.invoked_subcommand: Optional[Command] = invoked_subcommand
        self.subcommand_passed: Optional[str] = subcommand_passed
        self.command_failed: bool = command_failed
        self.current_parameter: Optional[inspect.Parameter] = current_parameter
        self._state: ConnectionState = self.message._state

    async def invoke(self, command: Command[CogT, P, T], /, *args: P.args, **kwargs: P.kwargs) -> T:
        r"""|coro|

        Calls a command with the arguments given.

        This is useful if you want to just call the callback that a
        :class:`.Command` holds internally.

        .. note::

            This does not handle converters, checks, cooldowns, pre-invoke,
            or after-invoke hooks in any matter. It calls the internal callback
            directly as-if it was a regular function.

            You must take care in passing the proper arguments when
            using this function.

        Parameters
        -----------
        command: :class:`.Command`
            The command that is going to be called.
        \*args
            The arguments to use.
        \*\*kwargs
            The keyword arguments to use.

        Raises
        -------
        TypeError
            The command argument to invoke is missing.
        """
        return await command(self, *args, **kwargs)

    async def reinvoke(self, *, call_hooks: bool = False, restart: bool = True) -> None:
        """|coro|

        Calls the command again.

        This is similar to :meth:`~.Context.invoke` except that it bypasses
        checks, cooldowns, and error handlers.

        .. note::

            If you want to bypass :exc:`.UserInputError` derived exceptions,
            it is recommended to use the regular :meth:`~.Context.invoke`
            as it will work more naturally. After all, this will end up
            using the old arguments the user has used and will thus just
            fail again.

        Parameters
        ------------
        call_hooks: :class:`bool`
            Whether to call the before and after invoke hooks.
        restart: :class:`bool`
            Whether to start the call chain from the very beginning
            or where we left off (i.e. the command that caused the error).
            The default is to start where we left off.

        Raises
        -------
        ValueError
            The context to reinvoke is not valid.
        """
        cmd = self.command
        view = self.view
        if cmd is None:
            raise ValueError('This context is not valid.')

        # some state to revert to when we're done
        index, previous = view.index, view.previous
        invoked_with = self.invoked_with
        invoked_subcommand = self.invoked_subcommand
        invoked_parents = self.invoked_parents
        subcommand_passed = self.subcommand_passed

        if restart:
            to_call = cmd.root_parent or cmd
            view.index = len(self.prefix or '')
            view.previous = 0
            self.invoked_parents = []
            self.invoked_with = view.get_word()  # advance to get the root command
        else:
            to_call = cmd

        try:
            await to_call.reinvoke(self, call_hooks=call_hooks)
        finally:
            self.command = cmd
            view.index = index
            view.previous = previous
            self.invoked_with = invoked_with
            self.invoked_subcommand = invoked_subcommand
            self.invoked_parents = invoked_parents
            self.subcommand_passed = subcommand_passed

    @property
    def valid(self) -> bool:
        """:class:`bool`: Checks if the invocation context is valid to be invoked with."""
        return self.prefix is not None and self.command is not None

    async def _get_channel(self) -> discord.abc.Messageable:
        return self.channel

    @property
    def clean_prefix(self) -> str:
        """:class:`str`: The cleaned up invoke prefix. i.e. mentions are ``@name`` instead of ``<@id>``.

        .. versionadded:: 2.0
        """
        if self.prefix is None:
            return ''

        user = self.me
        # this breaks if the prefix mention is not the bot itself but I
        # consider this to be an *incredibly* strange use case. I'd rather go
        # for this common use case rather than waste performance for the
        # odd one.
        pattern = re.compile(r"<@!?%s>" % user.id)
        return pattern.sub("@%s" % user.display_name.replace('\\', r'\\'), self.prefix)

    @property
    def cog(self) -> Optional[Cog]:
        """Optional[:class:`.Cog`]: Returns the cog associated with this context's command. None if it does not exist."""

        if self.command is None:
            return None
        return self.command.cog

    @discord.utils.cached_property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`.Guild`]: Returns the guild associated with this context's command. None if not available."""
        return self.message.guild

    @discord.utils.cached_property
    def channel(self) -> MessageableChannel:
        """Union[:class:`.abc.Messageable`]: Returns the channel associated with this context's command.
        Shorthand for :attr:`.Message.channel`.
        """
        return self.message.channel

    @discord.utils.cached_property
    def author(self) -> Union[User, Member]:
        """Union[:class:`~discord.User`, :class:`.Member`]:
        Returns the author associated with this context's command. Shorthand for :attr:`.Message.author`
        """
        return self.message.author

    @discord.utils.cached_property
    def me(self) -> Union[Member, ClientUser]:
        """Union[:class:`.Member`, :class:`.ClientUser`]:
        Similar to :attr:`.Guild.me` except it may return the :class:`.ClientUser` in private message contexts.
        """
        # bot.user will never be None at this point.
        return self.guild.me if self.guild is not None else self.bot.user  # type: ignore

    @property
    def voice_client(self) -> Optional[VoiceProtocol]:
        r"""Optional[:class:`.VoiceProtocol`]: A shortcut to :attr:`.Guild.voice_client`\, if applicable."""
        g = self.guild
        return g.voice_client if g else None

    async def send_help(self, *args: Any) -> Any:
        """send_help(entity=<bot>)

        |coro|

        Shows the help command for the specified entity if given.
        The entity can be a command or a cog.

        If no entity is given, then it'll show help for the
        entire bot.

        If the entity is a string, then it looks up whether it's a
        :class:`Cog` or a :class:`Command`.

        .. note::

            Due to the way this function works, instead of returning
            something similar to :meth:`~.commands.HelpCommand.command_not_found`
            this returns :class:`None` on bad input or no help command.

        Parameters
        ------------
        entity: Optional[Union[:class:`Command`, :class:`Cog`, :class:`str`]]
            The entity to show help for.

        Returns
        --------
        Any
            The result of the help command, if any.
        """
        from .core import Group, Command, wrap_callback
        from .errors import CommandError

        bot = self.bot
        cmd = bot.help_command

        if cmd is None:
            return None

        cmd = cmd.copy()
        cmd.context = self
        if len(args) == 0:
            await cmd.prepare_help_command(self, None)
            mapping = cmd.get_bot_mapping()
            injected = wrap_callback(cmd.send_bot_help)
            try:
                return await injected(mapping)
            except CommandError as e:
                await cmd.on_help_command_error(self, e)
                return None

        entity = args[0]
        if isinstance(entity, str):
            entity = bot.get_cog(entity) or bot.get_command(entity)

        if entity is None:
            return None

        try:
            entity.qualified_name
        except AttributeError:
            # if we're here then it's not a cog, group, or command.
            return None

        await cmd.prepare_help_command(self, entity.qualified_name)

        try:
            if hasattr(entity, '__cog_commands__'):
                injected = wrap_callback(cmd.send_cog_help)
                return await injected(entity)
            elif isinstance(entity, Group):
                injected = wrap_callback(cmd.send_group_help)
                return await injected(entity)
            elif isinstance(entity, Command):
                injected = wrap_callback(cmd.send_command_help)
                return await injected(entity)
            else:
                return None
        except CommandError as e:
            await cmd.on_help_command_error(self, e)

    @discord.utils.copy_doc(Message.reply)
    async def reply(self, content: Optional[str] = None, **kwargs: Any) -> Message:
        return await self.message.reply(content, **kwargs)


class InteractionContext:
    r"""Represents the context in which a application command is being invoked under.

    This class contains a lot of meta data to help you understand more about
    the invocation context. This class is not created manually and is instead
    passed around to commands as the first parameter.

    .. versionadded:: 2.0

    Attributes
    -----------
    interaction: :class:`.Interaction`
        The interaction that triggered the command being executed.
    bot: :class:`.Bot`
        The bot that contains the command being executed.
    args: :class:`list`
        The list of transformed arguments that were passed into the command.
        If this is accessed during the :func:`.on_command_error` event
        then this list could be incomplete.
    kwargs: :class:`dict`
        A dictionary of transformed arguments that were passed into the command.
        Similar to :attr:`args`\, if this is accessed in the
        :func:`.on_command_error` event then this dict could be incomplete.
    current_parameter: Optional[:class:`inspect.Parameter`]
        The parameter that is currently being inspected and converted.
        This is only of use for within converters.
    command: Optional[:class:`AppCommand`]
        The application command that is being invoked currently.
    invoked_parents: List[:class:`str`]
        The command names of the parents that triggered this invocation.

        For example in commands ``?a b c test``, the invoked parents are ``['a', 'b', 'c']``.
    invoked_subcommand: Optional[:class:`Command`]
        The application subcommand that was invoked.
        If no valid application subcommand was invoked then this is equal to ``None``.
    options_passed: Optional[:class:`Dict`]
        The options that where used to call a application subcommand. If nothing
        was passed to attempt a call to a subcommand then this is set to ``None``.
    command_failed: :class:`bool`
        A boolean that indicates if the command failed to be parsed, checked,
        or invoked.
    """

    def __init__(self,
                 *,
                 interaction: Interaction,
                 bot: BotT,
                 args: List[Any] = MISSING,
                 kwargs: Dict[str, Any] = MISSING,
                 view_item: Any = None,
                 command: Optional[AppCommand] = None,
                 invoked_parents: List[str] = MISSING,
                 invoked_subcommand: Optional[AppCommand] = None,
                 options_passed: Optional[Dict] = None,
                 command_failed: bool = False,
                 current_parameter: Optional[inspect.Parameter] = None,
                 ):
        self.interaction: Interaction = interaction
        self.bot: BotT = bot
        self.args: List[Any] = args or []
        self.kwargs: Dict[str, Any] = kwargs or {}
        self.view_item: Any = view_item
        self.command: Optional[AppCommand] = command
        self.invoked_parents: List[str] = invoked_parents or []
        self.invoked_subcommand: Optional[AppCommand] = invoked_subcommand
        self.options_passed: Optional[str] = options_passed
        self.command_failed: bool = command_failed
        self.current_parameter: Optional[inspect.Parameter] = current_parameter
        self._state: ConnectionState = self.interaction._state

    async def invoke(self, command: AppCommand[CogT, P, T], /, *args: P.args, **kwargs: P.kwargs) -> T:
        r"""|coro|

        Calls a application command with the arguments given.

        This is useful if you want to just call the callback that a
        :class:`.AppCommand` holds internally.

        .. note::

            This does not handle converters, checks, cooldowns, pre-invoke,
            or after-invoke hooks in any matter. It calls the internal callback
            directly as-if it was a regular function.

            You must take care in passing the proper arguments when
            using this function.

        Parameters
        -----------
        command: :class:`.Command`
            The command that is going to be called.
        \*args
            The arguments to use.
        \*\*kwargs
            The keyword arguments to use.

        Raises
        -------
        TypeError
            The command argument to invoke is missing.
        """
        return await command(self, *args, **kwargs)

    @property
    def valid(self) -> bool:
        """:class:`bool`: Checks if the invocation context is valid to be invoked with."""
        return self.command is not None

    async def _get_channel(self) -> discord.abc.Messageable:
        return self.channel

    @property
    def cog(self) -> Optional[Cog]:
        """Optional[:class:`.Cog`]: Returns the cog associated with this context's application command. None if it does not exist."""

        if self.command is None:
            return None
        return self.command.cog

    @discord.utils.cached_property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`.Guild`]: Returns the guild associated with this context's application command. None if not available."""
        return self.interaction.guild

    @discord.utils.cached_property
    def channel(self) -> MessageableChannel:
        """Union[:class:`.abc.Messageable`]: Returns the channel associated with this context's application command.
        Shorthand for :attr:`.Interaction.channel`.
        """
        return self.interaction.channel

    @discord.utils.cached_property
    def user(self) -> Union[User, Member]:
        """Union[:class:`~discord.User`, :class:`.Member`]:
        Returns the user associated with this context's application command. Shorthand for :attr:`.Interaction.user`
        """
        return self.interaction.user

    @discord.utils.cached_property
    def me(self) -> Union[Member, ClientUser]:
        """Union[:class:`.Member`, :class:`.ClientUser`]:
        Similar to :attr:`.Guild.me` except it may return the :class:`.ClientUser` in private message contexts.
        """
        # bot.user will never be None at this point.
        return self.guild.me if self.guild is not None else self.bot.user  # type: ignore

    @property
    def voice_client(self) -> Optional[VoiceProtocol]:
        r"""Optional[:class:`.VoiceProtocol`]: A shortcut to :attr:`.Guild.voice_client`\, if applicable."""
        g = self.guild
        return g.voice_client if g else None

    async def send_help(self, *args: Any) -> Any:
        #ToDo implement help command for app commands
        """send_help(entity=<bot>)

        |coro|

        Shows the help command for the specified entity if given.
        The entity can be a command or a cog.

        If no entity is given, then it'll show help for the
        entire bot.

        If the entity is a string, then it looks up whether it's a
        :class:`Cog` or a :class:`Command`.

        .. note::

            Due to the way this function works, instead of returning
            something similar to :meth:`~.commands.HelpCommand.command_not_found`
            this returns :class:`None` on bad input or no help command.

        Parameters
        ------------
        entity: Optional[Union[:class:`Command`, :class:`Cog`, :class:`str`]]
            The entity to show help for.

        Returns
        --------
        Any
            The result of the help command, if any.
        """
        from .core import AppGroup, AppCommand, wrap_callback
        from .errors import CommandError

        bot = self.bot
        cmd = bot.help_command

        if cmd is None:
            return None

        cmd = cmd.copy()
        cmd.context = self
        if len(args) == 0:
            await cmd.prepare_help_command(self, None)
            mapping = cmd.get_bot_mapping()
            injected = wrap_callback(cmd.send_bot_help)
            try:
                return await injected(mapping)
            except CommandError as e:
                await cmd.on_help_command_error(self, e)
                return None

        entity = args[0]
        if isinstance(entity, str):
            entity = bot.get_cog(entity) or bot.get_app_command(entity)

        if entity is None:
            return None

        try:
            entity.qualified_name
        except AttributeError:
            # if we're here then it's not a cog, group, or command.
            return None

        await cmd.prepare_help_command(self, entity.qualified_name)

        try:
            if hasattr(entity, '__cog_commands__'):
                injected = wrap_callback(cmd.send_cog_help)
                return await injected(entity)
            elif isinstance(entity, AppGroup):
                injected = wrap_callback(cmd.send_group_help)
                return await injected(entity)
            elif isinstance(entity, AppCommand):
                injected = wrap_callback(cmd.send_command_help)
                return await injected(entity)
            else:
                return None
        except CommandError as e:
            await cmd.on_help_command_error(self, e)

    async def reply(self, content: Optional[str] = None, **kwargs: Any) -> Message:
        """|coro|

        Sends a message to the given interaction.

        The content must be a type that can convert to a string through ``str(content)``.
        If the content is set to ``None`` (the default), then the ``embed`` parameter must
        be provided.

        To upload a single file, the ``file`` parameter should be used with a
        single :class:`~discord.File` object. To upload multiple files, the ``files``
        parameter should be used with a :class:`list` of :class:`~discord.File` objects.
        **Specifying both parameters will lead to an exception**.

        To upload a single embed, the ``embed`` parameter should be used with a
        single :class:`~discord.Embed` object. To upload multiple embeds, the ``embeds``
        parameter should be used with a :class:`list` of :class:`~discord.Embed` objects.
        **Specifying both parameters will lead to an exception**.

        Parameters
        ------------
        content: Optional[:class:`str`]
            The content of the message to send.
        tts: :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        embed: :class:`~discord.Embed`
            The rich embed for the content.
        file: :class:`~discord.File`
            The file to upload.
        files: List[:class:`~discord.File`]
            A list of files to upload. Must be a maximum of 10.
        nonce: :class:`int`
            The nonce to use for sending this message. If the message was successfully sent,
            then the message will have a nonce with this value.
        delete_after: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent. If the deletion fails,
            then it is silently ignored.
        allowed_mentions: :class:`~discord.AllowedMentions`
            Controls the mentions being processed in this message. If this is
            passed, then the object is merged with :attr:`~discord.Client.allowed_mentions`.
            The merging behaviour only overrides attributes that have been explicitly passed
            to the object, otherwise it uses the attributes set in :attr:`~discord.Client.allowed_mentions`.
            If no object is passed at all then the defaults given by :attr:`~discord.Client.allowed_mentions`
            are used instead.

            .. versionadded:: 1.4

        reference: Union[:class:`~discord.Message`, :class:`~discord.MessageReference`, :class:`~discord.PartialMessage`]
            A reference to the :class:`~discord.Message` to which you are replying, this can be created using
            :meth:`~discord.Message.to_reference` or passed directly as a :class:`~discord.Message`. You can control
            whether this mentions the author of the referenced message using the :attr:`~discord.AllowedMentions.replied_user`
            attribute of ``allowed_mentions`` or by setting ``mention_author``.

            .. versionadded:: 1.6

        mention_author: Optional[:class:`bool`]
            If set, overrides the :attr:`~discord.AllowedMentions.replied_user` attribute of ``allowed_mentions``.

            .. versionadded:: 1.6
        view: :class:`discord.ui.View`
            A Discord UI View to add to the message.
        embeds: List[:class:`~discord.Embed`]
            A list of embeds to upload. Must be a maximum of 10.

            .. versionadded:: 2.0
        stickers: Sequence[Union[:class:`~discord.GuildSticker`, :class:`~discord.StickerItem`]]
            A list of stickers to upload. Must be a maximum of 3.

            .. versionadded:: 2.0

        Raises
        --------
        ~discord.HTTPException
            Sending the message failed.
        ~discord.Forbidden
            You do not have the proper permissions to send the message.
        ~discord.InvalidArgument
            The ``files`` list is not of the appropriate size,
            you specified both ``file`` and ``files``,
            or you specified both ``embed`` and ``embeds``,
            or the ``reference`` object is not a :class:`~discord.Message`,
            :class:`~discord.MessageReference` or :class:`~discord.PartialMessage`.
        ~discord.InteractionResponded
            You already responded to the interaction.

        Returns
        ---------
        :class:`~discord.Message`
            The message that was sent.
        """

        return await self.interaction.response.send_message(content, **kwargs)

    async def reply_followup(self, content: Optional[str] = None, **kwargs: Any) -> Message:
        """|coro|

        Sends a followup message to the given interaction.

        The content must be a type that can convert to a string through ``str(content)``.
        If the content is set to ``None`` (the default), then the ``embed`` parameter must
        be provided.

        To upload a single file, the ``file`` parameter should be used with a
        single :class:`~discord.File` object. To upload multiple files, the ``files``
        parameter should be used with a :class:`list` of :class:`~discord.File` objects.
        **Specifying both parameters will lead to an exception**.

        To upload a single embed, the ``embed`` parameter should be used with a
        single :class:`~discord.Embed` object. To upload multiple embeds, the ``embeds``
        parameter should be used with a :class:`list` of :class:`~discord.Embed` objects.
        **Specifying both parameters will lead to an exception**.

        Parameters
        ------------
        content: Optional[:class:`str`]
            The content of the message to send.
        tts: :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        embed: :class:`~discord.Embed`
            The rich embed for the content.
        file: :class:`~discord.File`
            The file to upload.
        files: List[:class:`~discord.File`]
            A list of files to upload. Must be a maximum of 10.
        nonce: :class:`int`
            The nonce to use for sending this message. If the message was successfully sent,
            then the message will have a nonce with this value.
        delete_after: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent. If the deletion fails,
            then it is silently ignored.
        allowed_mentions: :class:`~discord.AllowedMentions`
            Controls the mentions being processed in this message. If this is
            passed, then the object is merged with :attr:`~discord.Client.allowed_mentions`.
            The merging behaviour only overrides attributes that have been explicitly passed
            to the object, otherwise it uses the attributes set in :attr:`~discord.Client.allowed_mentions`.
            If no object is passed at all then the defaults given by :attr:`~discord.Client.allowed_mentions`
            are used instead.

            .. versionadded:: 1.4

        reference: Union[:class:`~discord.Message`, :class:`~discord.MessageReference`, :class:`~discord.PartialMessage`]
            A reference to the :class:`~discord.Message` to which you are replying, this can be created using
            :meth:`~discord.Message.to_reference` or passed directly as a :class:`~discord.Message`. You can control
            whether this mentions the author of the referenced message using the :attr:`~discord.AllowedMentions.replied_user`
            attribute of ``allowed_mentions`` or by setting ``mention_author``.

            .. versionadded:: 1.6

        mention_author: Optional[:class:`bool`]
            If set, overrides the :attr:`~discord.AllowedMentions.replied_user` attribute of ``allowed_mentions``.

            .. versionadded:: 1.6
        view: :class:`discord.ui.View`
            A Discord UI View to add to the message.
        embeds: List[:class:`~discord.Embed`]
            A list of embeds to upload. Must be a maximum of 10.

            .. versionadded:: 2.0
        stickers: Sequence[Union[:class:`~discord.GuildSticker`, :class:`~discord.StickerItem`]]
            A list of stickers to upload. Must be a maximum of 3.

            .. versionadded:: 2.0

        Raises
        --------
        ~discord.HTTPException
            Sending the message failed.
        ~discord.Forbidden
            You do not have the proper permissions to send the message.
        ~discord.InvalidArgument
            The ``files`` list is not of the appropriate size,
            you specified both ``file`` and ``files``,
            or you specified both ``embed`` and ``embeds``,
            or the ``reference`` object is not a :class:`~discord.Message`,
            :class:`~discord.MessageReference` or :class:`~discord.PartialMessage`.
        ~discord.NotFound
            No existing webhook as there was no response to the interaction.

        Returns
        ---------
        :class:`~discord.Message`
            The message that was sent.
        """

        return await self.interaction.followup.send(content, **kwargs)

    @discord.utils.copy_doc(discord.abc.Messageable.send)
    async def send(self, content: Optional[str] = None, **kwargs: Any) -> Message:
        return await self.channel.send(content, **kwargs)
