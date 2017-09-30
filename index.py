import os

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
    return dbx.sharing_create_shared_link('/mixes/%s' % filename).url.replace('dl=0', 'dl=1')


def get_mixes():
    mixes_dir = os.path.expandvars('%HOME%/Music/mp3/mixes/me/')
    mixes = []
    for filename in os.listdir(mixes_dir):
        if filename.endswith('mp3'):

            mp3_filename = mixes_dir + filename
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

            cue_filename = mixes_dir + name + '.cue'
            tracks = []
            cue_link = None

            if os.path.exists(cue_filename):
                cue_link = _get_dropbox_link(name + '.cue')
                cuesheet = CueSheet()
                cuesheet.setOutputFormat('%performer% - %title%\n%file%\n%tracks%', '%performer% - %title%')
                with open(cue_filename) as f:
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


mixes = get_mixes()
write_template(mixes)
