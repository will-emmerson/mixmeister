import wave
from contextlib import closing
from os import listdir, path

DIR = r'C:\Users\will\Dropbox\mixes\BPH2017'
title = "BPH2017"
performer = "DJ Decimator"


def format_time(duration):
    minutes, remainder = divmod(duration, 60)
    seconds, remainder = divmod(remainder, 1)
    frames = remainder * 75
    return "%2.2d:%2.2d:%2.2d" % (minutes, seconds, frames)


def get_wav_duration(filename):
    with closing(wave.open(filename)) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)


def join_wavs():
    extension = "wav"
    output_file = path.join(DIR, '%s.%s' % (title, extension))
    with wave.open(output_file, 'wb') as output:

        for i, filename in enumerate(filenames):
            print('joining %s' % filename)
            wavfile = path.join(DIR, filename)
            with closing(wave.open(wavfile)) as f:
                if i == 0:
                    output.setparams(f.getparams())
                output.writeframes(f.readframes(f.getnframes()))


def write_cue_file():
    cuesheet = '''
TITLE "%s"
PERFORMER "%s"
FILE "%s.mp3" MP3''' % (title, performer, title)
    # NOTE: can't be lines in cue file or else it doesn't parse on phone
    current_time = 0

    for filename in filenames:
        d = {}
        print(filename)
        d['track'], d['title'], d['performer'] = filename.split(' - ')
        d['performer'] = d['performer'][:-4]

        d = {k: v.strip() for k, v in d.items()}

        d['time'] = format_time(current_time)
        wavfile = path.join(DIR, filename)
        duration = get_wav_duration(wavfile)
        print()
        format_time(duration)
        current_time += duration

        track_text = '''
TRACK %(track)s AUDIO
    PERFORMER "%(performer)s"
    TITLE "%(title)s"
    INDEX 01 %(time)s''' % d

        cuesheet += track_text

    print(cuesheet)

    filename = path.join(DIR, '%s.cue' % title)
    with open(filename, 'w') as f:
        f.write(cuesheet)
    print('wrote file %s' % filename)


filenames = [f for f in listdir(DIR) if f.startswith('0') and f.endswith('.wav')]
write_cue_file()
join_wavs()
