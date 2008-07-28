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
    sys.stdout('usage: ./gatrsky.py <username>\n')

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
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

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
        add_wrap_text(cell, date, row_h - 2)
        cell.refresh()
        cell.overwrite(screen)

    def fill_rows():
        cells[prev_cell].bkgdset(' ', curses.color_pair(1))
        cells[sel_cell].bkgdset(' ', curses.color_pair(2))
        for n, cell in enumerate(cells):
            fill_text(cell, entries[n + estart][0], entries[n + estart][1])

    while 1:
        # get entries, setup size info
        entries = get_entries()
        size = screen.getmaxyx()
        size = (size[Y] - 1, size[X]) # take 1 off for the status bar at bottom
        row_w = size[X]
        row_h = 140 / row_w + 3 # max chars for twitter = 140
        row_n = size[Y] / row_h

        # status bar
        statusbar = curses.newwin(1, row_w, size[Y], 0) # at the bottom
        message = 'WATCHING: ' + username + '  |  ' + '# OF TWEETS: ' + count
        statusbar.addnstr(0, 1, message, row_w - 2)
        statusbar.bkgdset(' ', curses.color_pair(3))
        statusbar.refresh()
        statusbar.overwrite(screen)

        # list of windows to use for entries
        cells = []
        for r in xrange(row_n):
            if len( cells ) < len( entries ): # dont make too many cells
                newcell = curses.newwin(row_h, row_w, r * row_h, 0)
                newcell.bkgdset(' ', curses.color_pair(1))
                cells.append(newcell)

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
            if c == ord('h'):
                # help will go away on next refresh
                statusbar.clear()
                helpmessage = 'q: quit | r: refresh | up/down arrows: scroll'
                statusbar.addnstr(0, 1, helpmessage, row_w - 2)
                statusbar.refresh()
            #t = time.time() - time1
            # auto update won't work, loop pauses to poll the keyboard
            #if t > updatetime and autoupdate == True:
            #    break

curses.wrapper(main)
