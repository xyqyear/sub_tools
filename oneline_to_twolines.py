# -*- encoding:utf-8 -*-

import os
import copy
import chardet

SEPARATOR = '`'
STYLE = '720P_Down_EN'


def parse_sub(sub_text):
    """
    解析ass字幕字符串
    :param sub_text:
    :return head_content: 字幕头部信息,无需处理
    :return infos_position: 每个元素所在的位置
    :return lines_list: 分割开了逗号之后的每个元素(后续处理直接','.join(lines_list)即可)
    """
    split_content = sub_text.split('[Events]\n')
    events = split_content[1]
    lines = events.split('\n')
    head_content = split_content[0] + '[Events]\n' + lines[0]
    format_text = lines[0].replace('Format:', '')
    speech_lines = [i.replace('Dialogue: ', '').split(',') for i in lines[1:] if i]

    infos = [i.strip() for i in format_text.split(',')]
    infos_position = {i: infos.index(i) for i in infos}
    lines_list = [i[:infos_position['Text']] + [','.join(i[infos_position['Text']:])] for i in speech_lines]

    return head_content, infos_position, lines_list


def restructure_sub(head_content, lines_list):
    """
    重新组合字幕内容
    :param head_content:
    :param lines_list:
    :return:
    """
    sub_str = '\n'.join([head_content] + ['Dialogue: ' + ','.join(element for element in line) for line in lines_list])
    return sub_str


def handle_sub(original_language_style, infos_position, lines_list):
    """
    复制一行并把style更改为所给出的源语言的style
    :param original_language_style:
    :param infos_position:
    :param lines_list:
    :return:
    """
    operating_lines_list = copy.deepcopy(lines_list)
    for line in lines_list:
        text = line[infos_position['Text']]
        if SEPARATOR not in text:
            continue
        text_list = text.split(SEPARATOR)
        original_text = text_list[0]
        translated_text = text_list[1]
        line_position = operating_lines_list.index(line)
        operating_lines_list.insert(line_position, line)
        operating_lines_list[line_position][infos_position['Text']] = original_text
        operating_lines_list[line_position][infos_position['Style']] = original_language_style
        operating_lines_list[line_position+1][infos_position['Text']] = translated_text

    return operating_lines_list


def save_sub(original_path, text, encoding):
    _dir, file = os.path.split(original_path)
    filename, ext = os.path.splitext(file)
    filename += '_separated'

    output_path = os.path.join(_dir, filename+ext)

    with open(output_path, 'w', encoding=encoding) as f:
        f.write(text)


def main():
    sub_file_path = input('请输入字幕文件路径:')
    with open(sub_file_path, 'rb') as f:
        encoding = chardet.detect(f.read())['encoding']

    with open(sub_file_path, encoding=encoding) as f:
        subtitle_text = f.read()

    head, infos, lines = parse_sub(subtitle_text)
    lines = handle_sub(STYLE, infos, lines)
    subtitle_text = restructure_sub(head, lines)
    save_sub(sub_file_path, subtitle_text, encoding)


if __name__ == '__main__':
    main()
