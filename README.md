# krita-plugins

For now the home of my one and only Krita plugin named AnimLayers, where you can animate specific layers in Krita. The animation is achieved by switching layer visibility rapidly.

## AnimLayers ##

### Install ###
You install the plugin by placing the animlayers folder and animlayers.desktop file in your pykrita folder. You can find the pykrita folder in the menu by going to *Settings -> Manage Resources...* and press the *Open Resources Folder* button.

### Instruction ###

You animate a specific range of layers by prefixing the layer name with the same letters. For example *PL * then all the layers where the name starts with *PL * will be part of the animation. In the AnimLayers window you enter *PL* in the Key field. You can also select a layer with the wanted key and press the *Get key* button.

![Picture](https://github.com/thomaslynge/krita-plugins/blob/master/img/animlayers_v1_1.png)

| Input | Description |
| --- | --- |
| *Key* | The layer starts with this key. |
| *Get key* | Get the key from the active layer. |
| *<* | Step one frame back. |
| *>* | Step one frame forward. |
| *Play/Stop* | Start and stop the animation. |
| *Pong loop* | If unchecked the animation runs from 0..n and starts over at frame 0. If checked the animation runs forth and back. |
| *Speed* | The speed of the animation in milliseconds. 1000 is one second per frame. |

#### Shortcuts
You can add shortcuts for Play and Step.
![Picture](https://github.com/thomaslynge/krita-plugins/blob/master/img/animlayersshortcuts.png)
