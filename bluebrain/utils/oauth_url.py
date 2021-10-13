import hikari
from typing import Any, Union, Iterable

class _MissingSentinel:
    def __eq__(self, other):
        return False

    def __bool__(self):
        return False

    def __repr__(self):
        return '...'


MISSING: Any = _MissingSentinel()


def oauth_url(
    client_id: Union[int, str],
    *,
    permissions: hikari.Permissions = MISSING,
    guild: hikari.Snowflake = MISSING,
    redirect_uri: str = MISSING,
    scopes: Iterable[str] = MISSING,
    disable_guild_select: bool = False,
) -> str:
    url = f'https://discord.com/oauth2/authorize?client_id={client_id}'
    url += '&scope=' + '+'.join(scopes or ('bot',))
    if permissions is not MISSING:
        url += f'&permissions={permissions.value}'
    if guild is not MISSING:
        url += f'&guild_id={guild.id}'
    if redirect_uri is not MISSING:
        from urllib.parse import urlencode

        url += '&response_type=code&' + urlencode({'redirect_uri': redirect_uri})
    if disable_guild_select:
        url += '&disable_guild_select=true'
    return url
