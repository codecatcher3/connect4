Connect-4
=========

This is the game of connect4 on the web. It was written to remind myself
of how to write 2-person strategy games. 

Then a crude web interface was written when I discovered the cool Brython
framework for putting python as a scripting language in place of Javascript.
It works but it is crude as I don't have a lot of time to spend improving
the UI.

I am aware that Connect-4 is trademarked. I am not making any money off
this. Can you write A.I.? If you can't, don't sue someone else who can.

Game Engine
===========
The game is written in an object oriented style. A simple alpha-beta search
engine is used. The evaluation function is simply the sum of squares of the
number of pieces formed in each line.

I am aware that the code can be optimized further.
