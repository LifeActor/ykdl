#!/usr/bin/env python
from argparse import ArgumentParser

def arg_parser():
    parser = ArgumentParser(description="You-Get, a video downloader. Forked form you-get 0.3.34@soimort")
    parser.add_argument('-l', '--playlist', action='store_true', default=False, help="Download as a playlist.")
    parser.add_argument('-i', '--info', action='store_true', default=False, help="Display the information of videos without downloading.")
    parser.add_argument('-u', '--url', action='store_true', default=False, help="Display the real URLs of videos without downloading.")
    parser.add_argument('-j', '--json', action='store_true', default=False, help="Display info in json format.")
    parser.add_argument('-F', '--format',  help="Video format code.")
    parser.add_argument('-o', '--output-dir', default='.', help="Set the output directory for downloaded videos.")
    parser.add_argument('-p', '--player', help="Directly play the video with PLAYER like vlc/smplayer")
    parser.add_argument('video_urls', type=str, nargs='+', help="video urls")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    print(arg_parser())
