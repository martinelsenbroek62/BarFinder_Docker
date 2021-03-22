import wave
import binascii
import time
import argparse


# format seconds into HH:MM:SS
def convert_seconds(sec):
    hh = str(int(sec // 3600))
    remains = sec % 3600
    mm = str(int(remains // 60))
    ss = str(round(remains % 60, 1))

    if len(hh) == 1:
        hh = '0' + hh
    if len(mm) == 1:
        mm = '0' + mm
    if len(ss.split('.')[0]) == 1:
        ss = '0' + ss
    return (hh, mm, ss)


def get_timestamp(path):
    print('path:', path)

    with wave.open(path, 'rb') as f:
        sample_rate = f.getframerate()

    with open(path, 'rb') as f:
        data = f.read()

    st_point = 0
    counts = len(data)

    print('counts:', counts)

    for i in range(counts - 20, 0, -1):
        # start point is 'adtllabl+'
        if data[i] == 97 and data[i + 1] == 100 and data[i + 2] == 116:
            if data[i + 3] == 108 and data[i + 4] == 108 and data[i + 5] == 97:
                if data[i + 6] == 98 and data[i + 7] == 108 and data[i + 8] == 43:
                    st_point = i
                    break

    print('st_point:', st_point)

    bookmarks = list()
    for i in range(st_point, counts):
        # finds 'labl' values
        if data[i] == 108 and data[i + 1] == 97:
            if data[i + 2] == 98 and data[i + 3] == 108:
                bookmarks.append({'index': i})

    print('bookmarks:', bookmarks)

    # gets values of each bookmark
    cnt_bookmakrs = len(bookmarks)

    print('cnt_bookmakrs:', cnt_bookmakrs)

    for i in range(cnt_bookmakrs):
        bookmarks[i]['tag'] = data[bookmarks[i]['index'] + 8]
        value = ''
        if i != (cnt_bookmakrs - 1):
            # gets values until next bookmark except for the last bookmark
            for j in range(bookmarks[i]['index'] + 12, bookmarks[i + 1]['index']):
                if data[j] == 0:
                    continue
                value += chr(data[j])
        else:
            for j in range(bookmarks[i]['index'] + 12, counts):
                if data[j] == 0:
                    continue
                value += chr(data[j])
        bookmarks[i]['value'] = value.strip()

    # print(bookmarks)

    # finds the address of position of bookmarks
    tmp_count = cnt_bookmakrs
    for i in range(bookmarks[0]['index'], 0, -1):
        if tmp_count == 0:
            break

        # finds the 'data' values
        if data[i] == 100 and data[i + 1] == 97:
            if data[i + 2] == 116 and data[i + 3] == 97:
                tmp_count -= 1
                bookmarks[tmp_count]['pos_index'] = i

    # print(bookmarks)

    # gets the position of each bookmark
    for each in bookmarks:
        hex_value = '0x'
        for j in range(each['pos_index'] + 15, each['pos_index'] + 11, -1):

            # concatenates each hex value
            if data[j] == 0:
                hex_value += (hex(data[j])[2:] + '0')
            elif data[j] < 10:
                hex_value += ('0' + hex(data[j])[2:])
            else:
                hex_value += hex(data[j])[2:]

        seconds = round(int(hex_value, 16) / sample_rate, 1)
        # fmt_seconds = convert_seconds(seconds)        
        each['pos'] = seconds

    # printing
    for each in bookmarks:
        print('{:50} \t\t {}'.format(each['value'], each['pos']))

    return bookmarks
