AmbilightParty
==============

## About

Turn your Ambilight Philips television into a fun device.

This project contains a JointSpace API wrapper to easily communicate with your Ambilight TV from your Python code.

Based on this library, AmbilightParty provides fun, customizable and extensible animations to enlight your living-room !


## Requirements

Python modules :
* ```requests```


## Get started
    $
    git clone https://github.com/pascalif/AmbilightParty
    cd AmbilightParty
    pip install -r requirements.txt
    python -m ambi.party --help


## How-to

## Using low-level API wrapper

There is so far a limited set of features implemented in the API wrapper.

```python
    tv = AmbiTV('192.168.0.59')
    tv.autoconfigure()
    tv.set_side(AmbiTV.TOP, 255, 0, 0)
    tv.set_pixel(AmbiTV.TOP, 2, 0, 255, 0)
```

## Using animations

The main function is just a demo on top of this library.
Many more to come !

```bash
    $ python -m ambi.party
```
