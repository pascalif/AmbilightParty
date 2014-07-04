AmbilightParty
==============

## About

Turn your Ambilight Philips television into a fun device.

This project contains a JointSpace API wrapper to easily communicate with your Ambilight TV from CLI or directly embedded in your Python code.

Based on this library, AmbilightParty provides fun, customizable and extensible animations to enlight your living-room!


## Requirements

Python modules :
* ```requests```


## Get started
    $
    git clone https://github.com/pascalif/AmbilightParty
    cd AmbilightParty
    pip install -r requirements.txt


## Using CLI

```bash
    $ python -m ambi.party --help

usage: party.py [-h] [--info] [--list] [--ip IP] [--stop]
                [--demo {basic,caterpillars,k2000}] [--color COLOR]
                [--caterpillar CATERPILLAR] [--direction {cw,ccw}]
                [--duration DURATION] [--speed SPEED]

Have fun with your Ambilight TV.

optional arguments:
  -h, --help            show this help message and exit
  --info                Display TV and library info
  --list                List available themes
  --ip IP               TV ip address
  --stop                Restore the TV in automatic Ambilight management mode
  --demo {basic,caterpillars,k2000}
                        Play a demo mode
  --color COLOR         Set a single color on all pixels. Format : RRGGBB, eg
                        FF8800
  --caterpillar CATERPILLAR
                        Name of the caterpillar to play
  --direction {cw,ccw}  Direction of caterpillar
  --duration DURATION   Duration of animation. None for forever
  --speed SPEED         Animation speed in milliseconds
```


## Using low-level library

There is so far a limited set of features implemented in the API wrapper.

```python
    tv = AmbiTV('192.168.0.59')
    tv.autoconfigure()
    tv.set_side(AmbiTV.TOP, 255, 0, 0)
    tv.set_pixel(AmbiTV.TOP, 2, 0, 255, 0)
```
