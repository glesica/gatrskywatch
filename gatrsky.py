import curses
import urllib2
import time
import sys
from xml.dom import minidom

if len( sys.argv ) == 2:
    username = sys.argv[1]
    count = '20'
elif len( sys.argv ) == 3:
    username = sys.argv[1]
    count = sys.argv[2]
else:
    sys.stdout('usage: ./gatrsky <username>\n')

url = 'http://twitter.com/statuses/user_timeline.xml?count=' + count + '&id=' + username
X = 1
Y = 0

def get_entries():
    rssfile = urllib2.urlopen(url)
    xmldoc = minidom.parseString(''.join(rssfile.readlines()))
    tweets = xmldoc.getElementsByTagName('status')
    entries = []
    for tweet in tweets:
        title = tweet.getElementsByTagName('text')[0].firstChild.data
        date = tweet.getElementsByTagName('created_at')[0].firstChild.data
        entries.append((title.encode('ascii'), date.encode('ascii')))
    return entries

def main(screen):
    oldcurs = curses.curs_set(0)

    updatetime = 5
    autoupdate = True

    def add_wrap_text(cell, text, startrow):
        i = 0
        row = startrow
        words = text.split()
        while len( words ) > 0:
            if row_w - i > len( words[0] ):
                cell.addstr(row, i, ' ' + words[0])
                i += len( words[0] ) + 1
                words.pop(0)
            else:
                row += 1
                i = 0

    def fill_text(cell, text, date):
        cell.clear()
        add_wrap_text(cell, text, 0)
        add_wrap_text(cell, date, row_h - 1)
        cell.refresh()
        cell.overwrite(screen)

    def fill_rows():
        cells[prev_cell].bkgdset(' ', curses.A_NORMAL)
        cells[sel_cell].bkgdset(' ', curses.A_STANDOUT)
        for n, cell in enumerate(cells):
            fill_text(cell, entries[n + estart][0], entries[n + estart][1])

    while 1:
        # get entries, setup size info
        entries = get_entries()
        size = screen.getmaxyx()
        row_w = size[X]
        row_h = 200 / size[1] + 2 # big number is just a guess, twitter max ~ 140, plus name
        row_n = size[Y] / row_h

        # list of windows to use for entries
        cells = []
        for r in xrange(row_n):
            cells.append(curses.newwin(row_h, row_w, r * row_h, 0))

        estart = 0 # first entry to read
        prev_cell = 0
        sel_cell = 0
        fill_rows()

        time1 = time.time()
        while 1:
            c = screen.getch()
            if c == ord('q'):
                curses.curs_set(oldcurs)
                return 0
            if c == curses.KEY_DOWN:
                if sel_cell < len( cells ) - 1:
                    prev_cell = sel_cell
                    sel_cell += 1
                elif (estart + len( cells )) < len( entries ):
                    estart += 1
                fill_rows()
            if c == curses.KEY_UP:
                if sel_cell > 0:
                    prev_cell = sel_cell
                    sel_cell -= 1
                elif estart > 0:
                    estart -= 1
                fill_rows()
            if c == ord('r'):
                break
            if c == ord('a'):
                autoupdate = not autoupdate
            t = time.time() - time1
            # auto update won't work, loop pauses to poll the keyboard
            #if t > updatetime and autoupdate == True:
            #    break

curses.wrapper(main)
