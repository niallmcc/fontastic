#!/bin/bash

python3 ../materialise.py --cache-folder /tmp

python3 ../materialise.py --cache-folder /tmp --svg-output-folder ./icons \
      --icon-names home folder  \
      --icon-styles outlined round

python3 ../materialise.py --cache-folder /tmp --svg-output-folder ./icons \
    --icon-names home folder --icon-styles outlined round \
    --icon-colours orange purple

python3 ../materialise.py --cache-folder /tmp --css-output-path icons.css \
    --icon-names home folder --icon-styles outlined round \
    --icon-colours orange purple

