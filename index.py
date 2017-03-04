import os
from cueparser import CueSheet
mixes_dir = os.path.expandvars('%HOME%/Music/mp3/mixes/me/')
output = ''
for filename in os.listdir(mixes_dir):
    if filename.endswith('cue'):
        filename = mixes_dir + filename
        cuesheet = CueSheet()
        cuesheet.setOutputFormat('%performer% - %title%\n%file%\n%tracks%', '%performer% - %title%')
        with open(filename) as f:
            cuesheet.setData(f.read())

        try:
            cuesheet.parse()
            for track in cuesheet.tracks:
                output += str(track).strip() + '\n'
        except:
            pass

with open('output.txt', 'w') as f:
    f.write(output)
