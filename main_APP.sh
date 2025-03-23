#!/bin/bash

python3 app.py 

# using file name path to specify each rinex file +-+-+-+-+-+-+-+-+-+-+-+-+-+-+
rinex_path="$1" 
export rinex_file_path="$rinex_path"
python3 precise_cor.py "$rinex_path"
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


