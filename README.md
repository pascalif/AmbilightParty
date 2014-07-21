AmbilightParty
==============

## About

Turn your **Ambilight Philips television** into a fun device.

This project contains a JointSpace API wrapper to easily communicate with your Ambilight TV from CLI or directly embedded into your own Python code.

Based on this library, AmbilightParty provides **fun, customizable and extensible animations** to enlight your living-room!

The library is compatible with 2-sides, 3-sides and newer 4-sides Philips TV equipped with Ambilight system.

You can watch a quick demo of some of the built-in effects and animations at **https://www.youtube.com/watch?v=iKO8UPjvpsg**


## Requirements

Python modules :
* ```requests```


## Get started

### Install from the sources
    $
    git clone https://github.com/pascalif/AmbilightParty
    cd AmbilightParty
    pip install -r requirements.txt

### Install from PIP
    $
    pip install ambilight


## Using CLI

If you installed the egg, you'll have this alias script installed :

```bash
    $ ambilight-party --help
```

In both cases, you can :

```bash
    $ python -m ambilight.party --help

usage: party.py [-h] [--info] [--list] [--ip IP] [--stop]
                [--demo {basic,caterpillars,k2000}] [--color COLOR]
                [--caterpillar CATERPILLAR] [--direction {cw,ccw}]
                [--flag FLAG] [--duration DURATION] [--speed SPEED]

Have fun with your Ambilight TV.

optional arguments:
  -h, --help            show this help message and exit
  --info                Display TV topology and library info
  --list                List available caterpillars and flags
  --ip IP               TV ip address
  --stop                Restore the TV in automatic Ambilight management mode
  --demo {basic,caterpillars,kitt}
                        Play a demo mode
  --color COLOR         Set a single color on all pixels. Format : RRGGBB, eg
                        FF8800
  --caterpillar CATERPILLAR
                        Name of the caterpillar to play
  --direction {cw,ccw}  Direction of caterpillar
  --flag FLAG           Name of the flag to display
  --flag-flicker FLAG_FLICKER
                        Number of flag flickering cycles. 0 to disabled the effect.
  --duration DURATION   Duration of animation. None for forever
  --speed SPEED         Animation steps speed in milliseconds
```

### Available built-in demos
- `basic` : a demonstration of calls to low-level API : change all pixels / by side / by pixel / by sub-pixel. Mirror and rotation effects.
- `caterpillars` : play a random subset of available caterpillars (see next section), each with random direction and speed.
- `kitt` : play the famous car's led animation

### Caterpillars

A caterpillar is a sequence of pixel colors, repeated all around your TV and animated with a rotation movement.

Caterpillars are configured in JSON file `data/caterpillars.json`. The file contains "country" (ie flags), some special events (christmas, halloween, St Patrick, ...) and misc ones ("traffic light, police car, RGB, rainbow, ...).

If you want to add your own caterpillars in the file, and due to the physical notion of light being additive, take care of duplicating some pixels - or inserting black pixels - to avoid a mix of colors on your wall between two contiguous pixels (see the difference between _rainbow_ and _rainbow2_).

From CLI, you can :
- get the list of available caterpillars with `--list`
- set the name of the caterpillar you want to play with `--caterpillar`
- set the sense of rotation with `--direction`
- set the speed of rotation with `--speed` (the greater, the slower - this is the delay between two steps)

### Flags

Thanks to `--flag`, you can project statically your favorite flag on the wall.
You can also make it blink when your team has scored a goal by adding the `--flag-flicker` argument!

Flags are described in JSON file `data/flags.json`.
So far, only two types of flags are taken into account by the code : those with 3 stripes either horizontally or vertically.

If your TV has only 2 sides equipped with LED, the vertical flag is not possible.
The horizontal flag will display differently whether you have 2, 3 or 4 LED sides.


## Using Python library

Classes are :
- **AmbilightTV** : **low-level wrapper of your TV JointSpace REST API**. It allows you to change completely the color of all pixels with `set_color()`,
  all sides at once (one color per side) with `set_sides()`, a given side with `set_side()` or a given pixel with `set_pixel()`.
  It can also change all pixels at once (one color per pixel) with `set_pixels_by_side()` method.

Quick example :

```python
    tv = AmbilightTV()

    # Retrieve TV topology
    tv.autoconfigure('192.168.0.59')
    # Switch off automatic mode
    tv.set_mode_manual()

    # Change every pixel or just a side
    tv.set_color(192, 28, 78)
    tv.set_side(AmbiTV.LEFT, 255, 0, 0)

    # Different ways of changing a pixel or sub-pixel value
    tv.set_pixel(AmbiTV.RIGHT, 2, 0, 128, 255)
    tv.set_pixel(AmbiTV.RIGHT, 2, color=(0, 255, 0))
    tv.set_pixel(AmbiTV.RIGHT, 4, blue=255)
```
See code of the built-in _basic_ demo to know more.

The AmbilightTV class offers a listener/observer mecanism to notify any object of pixels changes.


- **BufferedAmbilightTV** : a sub-class of the former with pixels **memory** capability. This class allows (so far) rotation and mirror effects, and basically any effect that needs to know the current state of the leds. It's using the listener feature of AmbilightTV to manage its pixels buffer.



- **AmbilightParty** : the class implementing **animations** needed by the CLI.


## Contribute

So many things could be improved and added such as powerful animations with :
- sun raising simulation, waves effect,
- more complex flags,
- integration with **Hue** system,
- use sound & channels Joinspace API,
- ...
Fork & play !
