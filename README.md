# HypixelProject

This project has two primary functionalities.
Firstly, given a minecraft username it can display information about how good the given player is at Hypixel Bedwars.
This is determined based on their statistics taken from the Hypixel API.
https://api.hypixel.net

Secondly, while in game it can take a screenshot of the tab menu, which contains all player usernames in the game.
Then it uses a homemade image to text translater relying on Minecraft's pixelated font to get the usernames as strings.
These usernames are then passed through the first functionality to find threatening players and displays a desktop notification when done.

I am currently working on another functionality:
To be able to take a screenshot of the screen using the default screen capture tool.
The program would then find the screenshot automatically and run the above functionality on it.
This has not yet been implemented.