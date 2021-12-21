import asyncio
import functools
import itertools
import math
import random

import discord
import youtube_dl
from async_timeout import timeout
from discord.ext import commands
import httpx
from bs4 import BeautifulSoup

from dotenv import load_dotenv
import os
import sys
import re
import time

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''
'''
load_dotenv()
token = os.getenv('discordToken')
'''
class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** BY **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('UNABLE TO LOCATE `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('UNABLE TO LOCATE `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('UNABLE TO FETCH `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))
        
        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @classmethod
    async def search_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        channel = ctx.channel
        loop = loop or asyncio.get_event_loop()

        cls.search_query = '%s%s:%s' % ('ytsearch', 10, ''.join(search))

        partial = functools.partial(cls.ytdl.extract_info, cls.search_query, download=False, process=False)
        info = await loop.run_in_executor(None, partial)

        cls.search = {}
        cls.search["title"] = f'Search results for:\n**{search}**'
        cls.search["type"] = 'rich'
        cls.search["color"] = 7506394
        cls.search["author"] = {'name': f'{ctx.author.name}', 'url': f'{ctx.author.avatar_url}', 'icon_url': f'{ctx.author.avatar_url}'}
        
        lst = []

        for e in info['entries']:
            #lst.append(f'`{info["entries"].index(e) + 1}.` {e.get("title")} **[{YTDLSource.parse_duration(int(e.get("duration")))}]**\n')
            VId = e.get('id')
            VUrl = 'https://www.youtube.com/watch?v=%s' % (VId)
            lst.append(f'`{info["entries"].index(e) + 1}.` [{e.get("title")}]({VUrl})\n')

        lst.append('\n**Type a number to make a choice, Type `cancel` to exit**')
        cls.search["description"] = "\n".join(lst)

        em = discord.Embed.from_dict(cls.search)
        await ctx.send(embed=em, delete_after=45.0)

        def check(msg):
            return msg.content.isdigit() == True and msg.channel == channel or msg.content == 'cancel' or msg.content == 'Cancel'
        
        try:
            m = await bot.wait_for('message', check=check, timeout=45.0)

        except asyncio.TimeoutError:
            rtrn = 'timeout'

        else:
            if m.content.isdigit() == True:
                sel = int(m.content)
                if 0 < sel <= 10:
                    for key, value in info.items():
                        if key == 'entries':
                            """data = value[sel - 1]"""
                            VId = value[sel - 1]['id']
                            VUrl = 'https://www.youtube.com/watch?v=%s' % (VId)
                            partial = functools.partial(cls.ytdl.extract_info, VUrl, download=False)
                            data = await loop.run_in_executor(None, partial)
                    rtrn = cls(ctx, discord.FFmpegPCMAudio(data['url'], **cls.FFMPEG_OPTIONS), data=data)
                else:
                    rtrn = 'sel_invalid'
            elif m.content == 'cancel':
                rtrn = 'cancel'
            else:
                rtrn = 'sel_invalid'
        
        return rtrn

    @staticmethod
    def parse_duration(duration: int):
        if duration > 0:
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)

            duration = []
            if days > 0:
                duration.append('{}'.format(round(days)))
                if hours < 10:
                    string = '0'+str(round(hours))
                else:
                    string = str(round(hours))
                duration.append(f'{string}')
                if minutes < 10:
                    string = '0'+str(round(minutes))
                else:
                    string = str(round(minutes))
                duration.append(f'{string}')
                if seconds < 10:
                    string = '0'+str(round(seconds))
                else:
                    string = str(round(seconds))
                duration.append(f'{string}')
                    
            else:
                if hours > 0:
                    duration.append(str(round(hours)))
                    if minutes < 10:
                        string = '0'+str(round(minutes))
                    else:
                        string = str(round(minutes))
                    duration.append(f'{string}')
                    if seconds < 10:
                        string = '0'+str(round(seconds))
                    else:
                        string = str(round(seconds))
                    duration.append(f'{string}')
                else:
                    if minutes > 0:
                        duration.append(str(round(minutes)))
                        if seconds < 10:
                            string = '0'+str(round(seconds))
                        else:
                            string = str(round(seconds))
                        duration.append(f'{string}')
                    else:
                        if seconds > 0:
                            duration.append(str(round(seconds)))
            
            value = ':'.join(duration)
        
        elif duration == 0:
            value = "LIVE"
        
        return value


class Song:
    __slots__ = ('source', 'requester','starttime','elapsed')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester
        self.starttime = time.perf_counter()
        self.elapsed = 0

    def stop(self):
        self.elapsed = time.perf_counter()-self.starttime

    def reset(self):
        self.elapsed = 0
        self.starttime = time.perf_counter()

    def resume(self):
        self.starttime = time.perf_counter()
    
    def create_embed(self):
        position = time.perf_counter()-self.starttime+self.elapsed
        minutes, seconds = divmod(position, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        position = []
        if days > 0:
            position.append('{}'.format(round(days)))
            if hours < 10:
                string = '0'+str(round(hours))
            else:
                string = str(round(hours))
            position.append(f'{string}')
            if minutes < 10:
                string = '0'+str(round(minutes))
            else:
                string = str(round(minutes))
            position.append(f'{string}')
            if seconds < 10:
                string = '0'+str(round(seconds))
            else:
                string = str(round(seconds))
            position.append(f'{string}')
                
        else:
            if hours > 0:
                position.append(str(round(hours)))
                if minutes < 10:
                    string = '0'+str(round(minutes))
                else:
                    string = str(round(minutes))
                position.append(f'{string}')
                if seconds < 10:
                    string = '0'+str(round(seconds))
                else:
                    string = str(round(seconds))
                position.append(f'{string}')
            else:
                if minutes > 0:
                    position.append(str(round(minutes)))
                    if seconds < 10:
                        string = '0'+str(round(seconds))
                    else:
                        string = str(round(seconds))
                    position.append(f'{string}')
                else:
                    if seconds > 0:
                        position.append(str(round(seconds)))
        
        pval = ':'.join(position)
        embed = (discord.Embed(title='ACTIVE SONG', description='```css\n{0.source.title}\n```'.format(self), color=discord.Color.blurple())
                .add_field(name='DURATION', value=f'{pval} / {self.source.duration}')
                .add_field(name='REQUESTER', value=self.requester.mention)
                .add_field(name='UPLOADER', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                .add_field(name='URL', value='[Click]({0.source.url})'.format(self))
                .set_thumbnail(url=self.source.thumbnail)
                .set_author(name=self.requester.name, icon_url=self.requester.avatar_url))
        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.exists = True

        self._loop = False
        self._autoplay = False
        self._volume = 0.5
        self.skip_votes = False

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def autoplay(self):
        return self._autoplay

    @autoplay.setter
    def autoplay(self, value: bool):
        self._autoplay = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()
            self.now = None
            if (self.loop == True and self.skip_votes == False):
                self.now = discord.FFmpegPCMAudio(self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS)
                self.voice.play(self.now, after=self.play_next_song)
                self.current.reset()
            else:
                # If autoplay is turned on wait 3 seconds for a new song.
                # If no song is found find a new one,
                # else if autoplay is turned off try to get the
                # next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                if self.autoplay:
                    try:
                        async with timeout(3): 
                            self.current = await self.songs.get()
                    except asyncio.TimeoutError:
                        # Spoof user agent to show whole page.
                        headers = {'User-Agent' : 'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'}
                        song_url = self.current.source.url
                        # Get the page
                        async with httpx.AsyncClient() as client:
                            response = await client.get(song_url, headers=headers)

                        soup = BeautifulSoup(response.text, features='lxml')

                        # Parse all the recommended videos out of the response and store them in a list
                        recommended_urls = []
                        for li in soup.find_all('li', class_='related-list-item'):
                            a = li.find('a')

                            # Only videos (no mixes or playlists)
                            if 'content-link' in a.attrs['class']:
                                recommended_urls.append(f'https://www.youtube.com{a.get("href")}')

                        ctx = self._ctx

                        async with ctx.typing():
                            try:
                                source = await YTDLSource.create_source(ctx, recommended_urls[0], loop=self.bot.loop)
                            except YTDLError as e:
                                await ctx.send('REQUEST ERROR: {}'.format(str(e)))
                                self.bot.loop.create_task(self.stop())
                                self.exists = False
                                return
                            else:
                                song = Song(source)
                                self.current = song
                                await ctx.send('QUEUED {}'.format(str(source)))
                        
                else:
                    try:
                        async with timeout(180):  # 3 minutes
                            self.current = await self.songs.get()
                    except asyncio.TimeoutError:
                        self.bot.loop.create_task(self.stop())
                        self.exists = False
                        return
                
                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)
                await self.current.source.channel.send(embed=self.current.create_embed())
            
            self.skip_votes = False
            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state or not state.exists:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('DIRECT MESSAGE COMMANDS FORBIDDEN')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('ERROR: {}'.format(str(error)))

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """CONNECT TO USER\'S AUDIO CHANNEL"""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='summon')
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """SUMMON BOT TO AUDIO CHANNEL"""

        if not channel and not ctx.author.voice:
            raise VoiceError('USER NOT CONNECTED TO CHANNEL, NO TARGET GIVEN')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave', aliases=['dcVC','disconnectVC'])
    async def _leave(self, ctx: commands.Context):
        """CONNECTION CLOSED"""

        if not ctx.voice_state.voice:
            return await ctx.send('BOT NOT CONNECTED TO AUDIO CHANNEL')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name='volume')
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """SETS VOLUME OF AUDIO PLAYBACK.
        PERCENTILE VALUE.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('NO AUDIO BEING PLAYED')

        if 0 > volume > 100:
            return await ctx.send('VOLUME OUTSIDE BOUNDS OF 0 AND 100')

        ctx.voice_state.volume = volume / 100
        await ctx.send('VOLUME SET TO {}%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing', 'nowplaying','np'])
    async def _now(self, ctx: commands.Context):
        """DETAILS OF CURRENT AUDIO PLAYBACK"""
        embed = ctx.voice_state.current.create_embed()
        await ctx.send(embed=embed)

    @commands.command(name='pause', aliases=['pa'])
    async def _pause(self, ctx: commands.Context):
        """HALT AUDIO PLAYBACK"""
        print(">>>Pause Command:")
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            ctx.voice_state.current.stop()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='resume', aliases=['re', 'res'])
    async def _resume(self, ctx: commands.Context):
        """RESUME AUDIO PLAYBACK"""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            ctx.voice_state.current.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='discardQueue', aliases=['dQ'])
    async def _stop(self, ctx: commands.Context):
        """DISCARDS CURRENT AUDIO AND QUEUE"""

        if ctx.voice_state.loop:
            ctx.voice_state.loop = not ctx.voice_state.loop
        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command(name='skip', aliases=['s'])
    async def _skip(self, ctx: commands.Context):
        """SKIP AUDIO.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send('NO AUDIO BEING PLAYED')
        ctx.voice_state.skip_votes = True
        await ctx.message.add_reaction('⏭')
        ctx.voice_state.skip()

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """DISPLAYS 10 ENTRIES OF QUEUE.
        PAGE VALUE CAN BE SPECIFIED.
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('NO ENTRIES IN QUEUE')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='PAGE {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle', aliases=['random','randomize'])
    async def _shuffle(self, ctx: commands.Context):
        """RANDOMIZE QUEUE ORDER"""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('NO ENTRIES IN QUEUE')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, index: int):
        """REMOVE FROM QUEUE AT INDEX"""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('NO ENTRIES IN QUEUE')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(name='loop')
    async def _loop(self, ctx: commands.Context):
        """ENGAGES LOOPING OF AUDIO.
        INVOKING COMMAND TOGGLES BEHAVIOR
        """
        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction('✅')
        await ctx.send('LOOPING NOW ' + ('ACTIVATED' if ctx.voice_state.loop else 'DEACTIVATED') )

    @commands.command(name='autoplay')
    async def _autoplay(self, ctx: commands.Context):
        """UPON END OF QUEUE, WILL QUEUE A RELATED SONG.
        SEARCH ALGORITHM IS... FLAWED.
        INVOKING COMMAND TOGGLES BEHAVIOR.
        """
        # Inverse boolean value to loop and unloop.
        ctx.voice_state.autoplay = not ctx.voice_state.autoplay
        await ctx.message.add_reaction('✅')
        await ctx.send('AUTOPLAY NOW ' + ('ACTIVATED' if ctx.voice_state.autoplay else 'DEACTIVATED') )

    @commands.command(name='play', aliases=['p', 'stream'])
    async def _play(self, ctx: commands.Context, *, search: str):
        """PLAYS AUDIO FROM EXTERIOR SOURCES
        IF OTHER AUDIO SOURCES ARE QUEUED, WILL QUEUE THIS AUDIO.
        """

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('REQUEST ERROR: {}'.format(str(e)))
            else:
                if not ctx.voice_state.voice:
                    await ctx.invoke(self._join)

                song = Song(source)
                await ctx.voice_state.songs.put(song)
                await ctx.send('QUEUED {}'.format(str(source)))

    @commands.command(name='searchYT')
    async def _search(self, ctx: commands.Context, *, search: str):
        """SEARCH YOUTUBE.
        RETURNS 10 RESULTS. REQUESTER CAN CHOOSE BY SPECIFYING INDEX.
        """
        async with ctx.typing():
            try:
                source = await YTDLSource.search_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('REQUEST ERROR: {}'.format(str(e)))
            else:
                if source == 'sel_invalid':
                    await ctx.send('INVALID SELECTION')
                elif source == 'cancel':
                    await ctx.send(':white_check_mark:')
                elif source == 'timeout':
                    await ctx.send('REQUEST IDLED TOO LONG')
                else:
                    if not ctx.voice_state.voice:
                        await ctx.invoke(self._join)

                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await ctx.send('QUEUED {}'.format(str(source)))
            
    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('USER NOT CONNECTED TO AUDIO CHANNEL')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('BOT CURRENTLY CONNECTED TO AUDIO CHANNEL')

'''
bot = commands.Bot(command_prefix='%', case_insensitive=True, description="This one should work. Not my own code, sadly.")
bot.add_cog(Music(bot))


@bot.event
async def on_ready():
    print('Logged in as:\n{0.user.name}\n{0.user.id}'.format(bot))

@bot.command(name='botstop', aliases=['bstop'])
#@has_permissions(kick_members = True)
async def botstop(ctx):
    print('death')
    await ctx.send('TERMINATED')
    await bot.close()
    return

@bot.command(name = 'reload', aliases = ['f5', 'refresh'], help = 'RELOAD')
async def reload(ctx):
    print('\nRELOADING ..........................\n')
    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

bot.run(token)
'''
