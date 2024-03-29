# Python-Snake-Game
This is a recreation of classical game snake made with python and the pygame library.

When you want to take a look at the source code you can download the main branch. The game as an executable or an app is a release.

## Requirements
You need to install the dependencies listed in requirements.txt if you don't already have it, in case you are executing the source code.
Pip has an implemented feature for automatically installing requirement lists. The command usually is `pip install -r requirements.txt`.

## Possible issues
On Windows you might get a dll error, as this game was packaged not on Windoes, but on Linux with wine, which has some dlls, which Windows doesn't provide. Just ignore the warning and close it. The game should still run.
On Linux you might have issues with the binary, as dependencies from pyinstaller/the packaged game might not be installed. If the binary doesn't run, you might try to install the dependencies if the game should list them. If not, you can download the source code and install the required python packages as listed above.

## Information for KDE-Plasma users
When you are using pygame windows in KDE Plasma the compositor gets blocked and all compositor animations stop working. If you still want the animations, you should go into the compositor settings and disable the option, that apps may block the compositor. (This is the last option in the compositor settings)

## Download game
The official game download can be found on the official [itch.io page](https://alpha-craft.itch.io/pysnake). You can also install it with the itch app for more convenience.
