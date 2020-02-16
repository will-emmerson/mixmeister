import json
import os
from pathlib import Path

import dropbox
from jinja2 import Environment, select_autoescape, FileSystemLoader
from mutagen.mp3 import MP3

from cueparser import CueSheet

dbx = dropbox.Dropbox(os.environ['DROPBOX_TOKEN'])


def write_template(mixes):
    env = Environment(loader=FileSystemLoader('.'), autoescape=select_autoescape(['html', 'xml']))
    env.get_template('template.html').stream(mixes=mixes).dump('index.html')


def _to_minutes(seconds):
    m, s = divmod(seconds, 60)
    return "%02d:%02d" % (m, s)


def _get_dropbox_link(filename):
    link = links.get(filename)
    if link:
        return link
    else:
        link = dbx.sharing_create_shared_link('/mixes/%s' % filename).url.replace('dl=0', 'dl=1')
        links[filename] = link
        return link


def get_mixes():
    mixes_dir = Path.home() / 'Dropbox' / 'mixes'
    mixes = []
    for filename in sorted(os.listdir(str(mixes_dir))):
        if filename.endswith('mp3'):

            mp3_filename = str(mixes_dir / filename)
            mp3_link = _get_dropbox_link(filename)
            name = filename[:-4]
            print(name)

            parts = name.split('-')
            if len(parts) > 1:
                anchor = parts[1]
            else:
                anchor = parts[0]
            anchor = anchor.strip().replace(' ', '-').replace('-[unmixed]', '').replace(',', '').lower()

            duration = _to_minutes(MP3(mp3_filename).info.length)

            cue_filename = str(mixes_dir / f'{name}.cue')
            tracks = []
            cue_link = None

            if os.path.exists(cue_filename):
                cue_link = _get_dropbox_link(name + '.cue')
                cuesheet = CueSheet()
                cuesheet.setOutputFormat('%performer% - %title%\n%file%\n%tracks%', '%performer% - %title%')
                with open(cue_filename, encoding='latin1') as f:
                    cuesheet.setData(f.read())
                cuesheet.parse()
                tracks = cuesheet.tracks

            mixes.append({
                'name': name,
                'anchor': anchor,
                'tracks': tracks,
                'duration': duration,
                'mp3_link': mp3_link,
                'cue_link': cue_link,
            })

    return mixes


try:
    with open('links.json') as f:
        links = json.load(f)
except FileNotFoundError:
    links = {}

mixes = get_mixes()
write_template(mixes)

with open('links.json', 'w') as f:
    json.dump(links, f)
