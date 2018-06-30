# krita-plugins

For now the home of my one and only Krita plugin named AnimLayers, where you can animate specific layers in Krita. The animation is achieved by switching layer visibility rapidly.

## AnimLayers ##

### Install ###
You install the plugin by placing the animlayers folder and animlayers.desktop file in your pykrita folder. You can find the pykrita folder in the menu by going to *Settings -> Manage Resources...* and press the *Open Resources Folder* button.

### Instruction ###

You animate a specific range of layers by prefixing the layer name with the same letters. For example *PL * then all the layers where the name starts with *PL * will be part of the animation. In the AnimLayers window you enter *PL* in the Key field.

*Key*
The layer starts with this key.

*Spd*
The speed of the animation in milliseconds. 1000 is one second per frame.

*Ping Pong*
If unchecked the animation runs from 0..n and starts over at frame 0. If checked the animation runs forth and back.

*Frame*
What frame should we stop at when stopping the animation. Frame 1 is 0. If left blank it does nothing.

*Step back*
Step one frame back.

*Step*
Step one frame forward.

*Play/Stop*
Start and stop the animation.

*Refresh frames*
Click this button if you have added or renamed frames.
