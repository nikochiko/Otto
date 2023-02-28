# Otto

A fun Discord bot that can make dog noises and connect you with people from different Discord servers.

Invite bot with this link: https://discord.com/api/oauth2/authorize?client_id=1079024533094273045&permissions=3213312&scope=bot

## What can it do?

### Matching with different channels across servers

This bot can match you with people in different channels and different servers who also ran the same command.

- `$matchme` -- Start a match-making session. Once a match is made, a bridge will be created between the two channels and all
messages will be relayed from one to the other.
- `$unmatch` -- Unmatch from the session. This will stop the relaying.

### Chess

This bot can create chess challenges for you on Lichess. The first two players to start the game with this link will get to play the game.

- `$chess` | `$chess 5+3` -- Create a link for a chess game with the given time control. By default it is 5+3.
- `$chess random` | `$chess random 5+3` -- Try to find a random match to play a chess game with, against someone else who ran the same command.
Note that the time control matching isn't strict (yet), and you may get matches with a different time control than specified.

### Voice

Bot can bark, meow, and if configured, make other noises too.

- `$bark` -- Join the voice channel you're in and make a barking noise
- `$meow` -- Join the voice channel you're in and make a cat's meowing noise
- `$disconnect` -- Disconnect from the voice channel it is in
- `$join` -- Join the voice channel you're in

### Spotify

Bot can connect with your Spotify and do things with it. For now it can only tell you what song you are currently listening to, but more functionality
can be added in the future as it seems useful.

- `$spotify connect` -- Get an OAuth URL that can be used to hand the bot an API key for getting your data
- `$spotify status` -- Use this token to get status of what you're currenly playing. Replies with an embed of the track name, album name, album cover image, and an audio preview.

### Others

`$otto` -- This is a ping kind of test command. Otto should reply to this with a "Hello!" if it is working.

When a message contains the word "otto", it will reply to it with a barking message
as text. This is just for looking cute.

When a message contains the words "send pics" or "send nudes" it will send a random
dog picture.

## Deployment

### Requirements:

- **python >= 3.10**
- **ffmpeg**

### Setup steps:

1. Run `make deps`. If your default python3 points to a version that is less than python3.10, install the newer version along with its
the package needed for venv, and modify the `venv` command in Makefile from `python3 -m venv venv` to `python3.x -m venv venv`. Substitute 3.x for the newer version that you installed.
2. Copy `otto/config.sample.py` to `otto/config.py` and fill in the bot token or other details that might be configurable.
3. Run `make run`, or use a supervisor/systemd service to do this on every startup.

Bot is running now!

## LICENSE

Licensed under MIT License.
