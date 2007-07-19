Pinyin Keyboard
Author: YIN Dian
Project Homepage: http://code.google.com/p/pinyinkey

Pinyin Keyboard (abbr: pinyinkey) is an auxiliary tool for inputing Pinyin
with tone markers. It works like an IME, but actually not --- you can only
input toned Pinyin within the program's GUI window, not in other applications.
The GUI is simple, as it is not designed to be a functional complete text
editor, but simply an auxiliary tool allowing you to input toned Pinyin and
copy them to other locations you want.

This project is inspired by the telex input method for Vietnamese, and
originated from my attempt on pyformat.py, a simple formatter for toned
Pinyin, which was first publicized at the colledge BBS[1]. Then I found using
the CLI tool is rather painful and wrote a simple GUI afterwards. As time goes
I then implemented Vietnamese input and improved what I've done from time to
time. 

Now the tool natively supports the input of Chinese Pinyin and Vietnamese. The
input rule is simple: just specify the tone using the tone marker in any place
after the first vowel in the syllable to get the syllable toned. The rules are
specified in rule files, and they are quite straightforward and easy to modify
for your own need. I think it makes the input of romanization transliterations
of various Chinese dialects much easier:)

Enough now, so just run gui.py and enjoy yourselves!

Reference:
[1]: http://bbs.ustc.edu.cn/cgi/go?cgi=bbscon&bid=355&fn=M467CCDEB
