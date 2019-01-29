# sub_tools
这是一个双语字幕的小工具(适用于.ass)

## insert_translate_line.py
代码辣鸡,在没啥时间的情况下写出来的\
用于在英文字幕写完之后在英文字幕后插入中文空行

## auto_recognize.py
依赖: 

    SpeechRecognition  (pip install SpeechRecognition)
    ffmpeg             (pip install ffmpeg-python)

如果懒得做双语字幕,可以先做完英文字幕\
然后利用这个,用google语音识别自动识别出英文字幕\
当然还是会出错的,但是总比从头开始写英文字幕好吧

添加了百度语音识别(中文)支持\
需要百度语音识别的 API Key 和 Secret Key\
提示: Secret Key复制的时候可能最后会带个空格,需要把最后的空格去掉

使用百度语音识别方法:\
1.打开get_baidu_token.py, 修改api_key和secret_key\
2.出现了baidu.token文件后即可使用auto_recognize.py\
3.运行auto_recognize.py时输入引擎为 baidu