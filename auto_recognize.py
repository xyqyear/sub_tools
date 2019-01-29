# -*- encoding:utf-8 -*-

import re
import os
import copy
import time
import json
import uuid
import base64
import ffmpeg
import chardet
import requests
import speech_recognition as sr

STYLE = '720P_Down_EN'
SUB_FILE_PATH = r""
AUDIO_FILE_PATH = r""
MODE = '1'
ENGINE = ''


def merge_list(list1, list2):
    """
    长度相同的列表穿插合并
    :param list1:
    :param list2:
    :return:
    """
    length = len(list1)
    out_list = list()
    for i in range(length):
        out_list.append(list1[i])
        out_list.append(list2[i])

    return out_list


def to_second(sub_time):
    time_tuple = re.findall(r'(\d+):(\d+):(\d+)\.(\d+)', sub_time)[0]
    time_tuple = [int(i) for i in time_tuple]
    h = time_tuple[0]
    mm = time_tuple[1]
    ss = time_tuple[2]
    f = time_tuple[3]
    return h * 3600 + mm * 60 + ss + f / 100


def parse_sub(sub_text=str()):
    """
    解析ass字幕字符串
    :param sub_text:
    :return:
    """
    splited_content = sub_text.split('[Events]\n')
    head_content = splited_content[0]
    events = splited_content[1]
    lines = events.split('\n')
    format_text = lines[0].replace('Format:', '')
    speech_lines = [i.replace('Dialogue: ', '').split(',') for i in lines[1:] if i]

    formats = [i.strip() for i in format_text.split(',')]
    formats = {i: formats.index(i) for i in formats}
    lines_list = [i[:formats['Text']] + [','.join(i[formats['Text']:])] for i in speech_lines]

    return head_content, formats, lines_list


def ffmpeg_cut_pcm(audio_file_path, offset, duration):
    audio_bytes, _ = (ffmpeg
                      .input(audio_file_path)
                      .output('-', format='s16le', acodec='pcm_s16le', ac=1, ar='16k', ss=offset, t=duration)
                      .run(capture_stdout=True)
                      )
    return audio_bytes


def recognize_baidu_one_piece(audio_bytes, token):
    url = "http://vop.baidu.com/server_api"
    speech_length = len(audio_bytes)
    speech = base64.b64encode(audio_bytes).decode("utf-8")
    mac_address = uuid.UUID(int=uuid.getnode()).hex[-12:]
    data = {
        "format": "pcm",
        "rate": 16000,
        "channel": 1,
        "cuid": mac_address,
        "token": token,
        "dev_pid": 1536,
        "speech": speech,
        "len": speech_length,
    }
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    # debug
    print(r.text)
    return json.loads(r.text)['result']


def recognize(formats, sub_lines, audio_file_path, engine):
    pieces = list()
    results = list()

    for line in sub_lines:
        start_time = to_second(line[formats['Start']])
        end_time = to_second(line[formats['End']])
        pieces.append({'offset': start_time, 'duration': end_time - start_time})

    if engine == 'google':
        audio_obj = sr.AudioFile(audio_file_path)
        recognizer = sr.Recognizer()
        for piece in pieces:
            with audio_obj as obj:
                offset = piece['offset']
                duration = piece['duration']
                print('offset:{}, duration:{}'.format(offset, duration))
                audio = recognizer.record(obj, offset=offset, duration=duration)
                result = '*fail*'
                while True:
                    try:
                        result = recognizer.recognize_google(audio)
                        break
                    except sr.RequestError:
                        continue
                    except sr.UnknownValueError:
                        break

                print('result:{}'.format(result))
                results.append(result)
                time.sleep(3)

    elif engine == 'baidu':
        with open('baidu.token', 'r', encoding='utf-8') as token_file:
            token = token_file.read()

        for piece in pieces:
            offset = piece['offset']
            duration = piece['duration']
            print('offset:{}, duration:{}'.format(offset, duration))
            result = '*fail*'

            audio_bytes = ffmpeg_cut_pcm(audio_file_path, offset, duration)
            try:
                result_list = recognize_baidu_one_piece(audio_bytes, token)
                if result_list:
                    result = result_list[0]
            # temporarily
            except Exception as e:
                print(e)

            print('result:{}'.format(result))
            results.append(result)
            time.sleep(3)

    return results


def restructure_sub(head, formats, original_lines, recognize_result, mode, style):
    result_lines = list()
    if mode == '1':
        new_lines = copy.deepcopy(original_lines)
        for i in range(len(original_lines)):
            new_lines[i][formats['Style']] = style
            new_lines[i][formats['Text']] = recognize_result[i]

        result_lines = merge_list(new_lines, original_lines)

    elif mode == '2':
        for i in range(len(original_lines)):
            original_lines[i][formats['Style']] = style
            original_lines[i][formats['Text']] = recognize_result[i]

        result_lines = original_lines

    result_sub_text = head + '[Events]\n' + restructure_event(formats, result_lines)
    return result_sub_text


def restructure_event(formats, lines):
    format_text = 'Format: ' + ', '.join(formats)
    dialogue_text = '\n'.join(['Dialogue: ' + ','.join(line) for line in lines])

    return '\n'.join([format_text, dialogue_text])


def save_sub(original_path, text, encoding):
    _dir, file = os.path.split(original_path)
    filename, ext = os.path.splitext(file)
    filename += 'recognized'

    output_path = os.path.join(_dir, filename+ext)

    with open(output_path, 'w', encoding=encoding) as f:
        f.write(text)


def main():
    if SUB_FILE_PATH:
        sub_file_path = SUB_FILE_PATH
    else:
        sub_file_path = input('请输入字幕文件路径:')
        if '"' in sub_file_path:
            sub_file_path = sub_file_path.replace('"', '')

    if AUDIO_FILE_PATH:
        audio_file_path = AUDIO_FILE_PATH
    else:
        audio_file_path = input('请输入音频文件路径:')
        if '"' in audio_file_path:
            audio_file_path = audio_file_path.replace('"', '')

    if MODE:
        mode = MODE
    else:
        mode = input('请输入操作模式\n1是将英文字幕穿插入原文,自定义英文字幕样式,\n2是直接替换原文\n请输入字符:')

    if STYLE:
        style = STYLE
    else:
        style = input('请输入英文字幕样式:')

    if ENGINE:
        engine = ENGINE
    else:
        engine = input('请输入识别引擎(google代表谷歌识别,baidu代表百度语音识别):')

    with open(sub_file_path, 'rb') as f:
        encoding = chardet.detect(f.read())['encoding']

    with open(sub_file_path, encoding=encoding) as f:
        subtitle_text = f.read()

    sub_head, formats, lines = parse_sub(subtitle_text)
    recognize_result = recognize(formats, lines, audio_file_path, engine)
    result_sub_text = restructure_sub(sub_head, formats, lines, recognize_result, mode, style)
    save_sub(sub_file_path, result_sub_text, encoding)


if __name__ == '__main__':
    main()
