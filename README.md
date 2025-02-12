# 🐈 Cat Collector Bot 🐈‍⬛

This is a Twitch and Discord bot written in Python that serves the amazing purpose of spawning silly little cat emotes in Twitch chat for viewers to collect.

The Discord bot can connect to users' Twitch accounts and display their cat collection in a discord server!

See if you can catch them all =^w^=

# Usage

## Running from binary release

Coming soon...

## Running from source

### Linux & MacOS
Prerequisites: git, python3.13.1+

1. Open a terminal
1. Clone the repository and go inside the cloned directory
    ```bash
    git clone https://github.com/AnicJov/CatCollector && cd CatCollector
    ```
1. Create a Python virtual environment
    ```bash
    python -m venv venv
    ```
1. Install dependencies
    ```bash
    venv/bin/pip install -r requirements.txt
    ```
1. Follow the instruction bellow to configure the environment
1. Run the bots
    ```bash
    venv/bin/python twitch_bot.py
    ```
    ```bash
    venv/bin/python discord_bot.py
    ```

### Windows
Prerequisites: [Git](https://git-scm.com/downloads/win), [Python](https://www.python.org/downloads/windows/), [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
1. Open a Powershell window
1. Clone the repository and go inside the cloned directory
    ```ps1
    git clone https://github.com/AnicJov/CatCollector && cd CatCollector
    ```
1. Create a Python virtual environment and activate it
    ```ps1
    python -m venv venv && .\venv\Scripts\Activate.ps1
    ```
    > Note:
    > It may be required to change the execution policy on your system in order to activate the virtual environment
    >
    > `PS C:\> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
1. Install dependencies
    ```ps1
    pip install -r requirements.txt
1. Follow the instruction bellow to configure the environment
1. Run the bots
    ```ps1
    venv/bin/python twitch_bot.py
    ```
    ```ps1
    venv/bin/python discord_bot.py
    ```   ```

### Environment setup

Create a `.env` file in the project directory.
Open the file in a text editor and enter the required information in the following format:

```env
DISCORD_TOKEN={YOUR_DISCORD_TOKEN}
TWITCH_TOKEN={YOUR_TWITCH_TOKEN}
CHANNELS={LIST_OF_CHANNEL_TO_JOIN} # Separated by ,
SPAWN_INTERVAL=60,120 # In minutes
CATCH_INTERVAL=120 # In seconds
TWITCH_JOIN_MESSAGE=hiHelloHi:)
DISCORD_CHANNELS_ANNOUNCE=bot-stuff,botspam,commands,bot,bot-commands,bot-setup
DISCORD_JOIN_MESSAGE=<a:hiHelloHi:1339048539363344407>
LINK_CODE_EXPIRATION=600 # In seconds
```

# Credits

Thanks to [KrypticSR](https://www.twitch.tv/krypticsr) for the idea!

# Help & Contributing
If you're interested in contributing or have a good idea for a fix or feature feel free to open an issue/PR here on GitHub or reach out to me on Discord at `_anic`.

Keep in mind that the code was written very hastily and is not of very good quality yet!
