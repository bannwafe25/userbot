from clients import navy
from command import (channelplay_cmd, end_cmd, group_call_ends, pause_cmd,
                     play_cmd, playlist_cmd, resume_cmd, skip_cmd, volume_cmd)
from helpers import CMD

__MODULES__ = "Music"
__HELP__ = """<blockquote>Command Help **Music**</blockquote>
<blockquote expandable>--**Basic Commands**--
    **Use `v` for play video**
        `{0}play` (title)
        `{0}vplay` (title)
    **Resume playing**
        `{0}resume`
    **Pause playing**
        `{0}pause`
    **Skip playing**
        `{0}skip`
    **End playing**
        `{0}end`</blockquote>
        
<blockquote expandable>--**Channels Commands**--
    **Playing to channel, use `v` for playing video**
        `{0}cplay` (title) 
        `{0}cvplay` title
    **Resume playing channel**
        `{0}cresume`
    **Pause playing channel**
        `{0}cpause`
    **Skip playing channel**
        `{0}cskip`
    **End playing channel**
        `{0}cend`
    **Linked channel to chat**
        `{0}channelplay linked`
    **Disable linked channel**
        `{0}channelplay disable`
    **Check linked playback channel**
        `{0}channelplay status`</blockquote>    

<b>   {1}</b>"""


@CMD.UBOT("play|vplay|cplay|cvplay")
async def _(client, message):
    return await client.send_message(
        message.chat.id,
        "<b>Jika ingin demus silahkan gunakan @flomusik_bot</b>"
    )


