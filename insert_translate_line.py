# -*- encoding:utf-8 -*-
import sys
import chardet


def get_line_infos(line, formats):
    try:
        line_infos = line.split(':', 1)[1].split(',', len(formats)-1)
        return line_infos

    except Exception:
        return ''


def get_line_info(line, formats, format_):
    try:
        line_infos = get_line_infos(line, formats)
        index = formats.index(format_)
        line_info = line_infos[index]
        return line_info

    except Exception:
        return ''


def gen_new_line(last_line, formats):
    line_infos = get_line_infos(last_line, formats)
    style_index = formats.index('Style')
    text_index = formats.index('Text')
    line_infos[style_index] = new_style
    line_infos[text_index] = ''
    new_line = 'Dialogue:' + ','.join(line_infos)

    return new_line


def handle_sub(sub):
    lines = sub.split('\r\n')
    lines_handled = list()
    got_events = False
    formats = list()
    last_line = ''
    for line in lines:
        if not got_events:
            if '[Events]' in line:
                got_events = True

        else:
            if line.startswith('Format'):
                formats = line.split(':')[1].split(',')
                formats = [i.replace(' ', '') for i in formats]

            else:
                line_style = get_line_info(line, formats, 'Style')
                last_line_style = get_line_info(last_line, formats, 'Style')
                # 如果上一行是英文行
                # 如果这一行是中文行就跳过
                # 否则就在这一行之前插入一行上一行的复制,并且去掉Text,替换Style为新的Style
                if 'EN' in last_line_style:
                    if 'CN' in line_style:
                        print(line, '\n---CN')
                    else:
                        new_line = gen_new_line(last_line, formats)
                        lines_handled.append(new_line)
                        print(new_line, '\n---Inserted')

                last_line = line

        lines_handled.append(line)

    new_sub = '\n'.join(lines_handled)
    return new_sub


if __name__ == '__main__':
    if len(sys.argv) > 1:
        sub_path = sys.argv[1]
    else:
        sub_path = input('Please input the file path of subtitle:')
    new_style = input('please input the Style that would be used to insert lines:')
    with open(sub_path, 'rb') as old_file:
        old_sub_raw = old_file.read()
        print(old_sub_raw)
        encoding = chardet.detect(old_sub_raw)['encoding']
        old_sub = old_sub_raw.decode(encoding)
        new_sub = handle_sub(old_sub)

    with open(sub_path+'.bak', 'w', encoding=encoding) as old_file_bak:
        old_file_bak.write(old_sub)
    with open(sub_path, 'w', encoding=encoding) as new_file:
        new_file.write(new_sub)
