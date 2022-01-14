#!/usr/local/bin/python
# encoding=utf-8

import sys
import codecs
import chardet
import re


def read_then_write(in_file, guess_encoding, out_encoding):
    dot_pos = in_file.rfind('.')
    output_file = in_file[0:dot_pos] + '(%s)' % out_encoding + in_file[dot_pos:]
    writer = open(output_file, 'wb')
    reader = open(in_file, 'rb')
    for line in reader:
        try:
            line = codecs.decode(line, guess_encoding)
            encoded_line = codecs.encode(line, out_encoding)
            writer.write(encoded_line)
        except Exception as e:
            pass
    reader.close()
    writer.close()


def extract_info(info_file):
    """
    Extract album title, performer and song names from the given album info. file
    :param info_file:
    :return: (title, performer, [(no, song1), (no, song2), ...])
    """
    reader = open(info_file, 'rb')
    confidence, guess_encoding = detect(info_file)
    songs = []
    has_title = False
    has_performer = False
    for line in reader:
        line = line.strip()
        try:
            line = codecs.decode(line, guess_encoding)
            if not has_title and (line.startswith(u"专辑名称：") or line.startswith(u"唱片名称：")):
                title = line[5:]
                has_title = True
            elif not has_performer and line.startswith(u"歌手："):
                performer = line[3:]
                has_performer = True
            elif not has_performer and line.startswith(u"歌手组合："):
                performer = line[5:]
                has_performer = True
            elif re.match("^\d\d .+", line):
                pos = line.index(' ')
                no = line[:pos]
                name = line[pos+1:]
                songs.append((no, name))
        except Exception as e:
            print ('Exception: err while process line: ' + line)
    reader.close()
    return title, performer, songs


def rebuild(in_file, info_file):
    """
    Rebuild the cue file with the given album info file.
    """
    out_encoding = 'utf-8'

    title, performer, songs = extract_info(info_file)

    album_cue = read_file_as_string(in_file)

    # put on title
    album_cue = album_cue.replace(u"\"未知标题\"", "\"" + title + "\"")
    # put on performer
    album_cue = album_cue.replace(u"\"未知艺术家\"", "\"" + performer + "\"")
    # put on all songs' names
    for song_name in songs:
        no, name = song_name
        old_name = "Track" + str(no)
        album_cue = album_cue.replace(old_name, name)

    dot_pos = in_file.rfind('.')
    output_file = in_file[0:dot_pos] + '(%s)' % out_encoding + in_file[dot_pos:]
    writer = open(output_file, 'wb')
    encoded_line = codecs.encode(album_cue, out_encoding)
    writer.write(encoded_line)
    writer.close()


def read_file_as_string(in_file):
    confidence, guess_encoding = detect(in_file)
    reader = open(in_file, 'r')
    text = []
    for line in reader:
        line = codecs.decode(line, guess_encoding)
        text.append(line)
    return ''.join(text)


def convert(in_file, out_encoding):
    confidence, guess_encoding = detect(in_file)
    read_then_write(in_file, guess_encoding, out_encoding)
    print( 'Convert from %s to %s Completed (with a confidence of %.2f%%)!' \
              % (guess_encoding, out_encoding, confidence))


def detect(in_file):
    with open(in_file, 'rb') as f:
        result = chardet.detect(f.read())
        confidence = float(result['confidence']) * 100
        guess_encoding = result['encoding']
    return confidence, guess_encoding


def print_usage():
    print( 'Usage: ')
    print( '       python cow.py [detect/convert] input_file [output_encoding(default: utf-8)] 检测/转换文件到指定编码')
    print( '       python cow.py rebuild cue_file album_info_file 使用专辑信息补全cue文件信息')


if __name__ == '__main__':
    arg_num = len(sys.argv)
    if arg_num > 2:
        a_type = sys.argv[1]
        input_file = sys.argv[2]
        output_encoding = 'utf-8'
        if a_type == 'detect':
            g_confidence, g_encoding = detect(input_file)
            print( 'Guess encoding: %s (with a confidence of %.2f%%).' % (g_encoding, g_confidence))
        elif a_type == 'convert':
            if arg_num > 3:
                output_encoding = sys.argv[3]
            convert(input_file, output_encoding)
        elif a_type == 'rebuild':
            album_info_file = sys.argv[3]
            rebuild(input_file, album_info_file)

    else:
        print_usage()
