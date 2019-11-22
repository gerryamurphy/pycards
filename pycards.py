# -*- coding: utf-8 -*-

import sqlite3
import time
import logging
import os
import readchar

# encoding for german "frÃ¶hlich:
#cvs files as well as tab
#import from dict.cc
# select topics
# cleanup menus
#review stats
#users
__version__ = '0.4'

LEITNER_BOXES = 5

class Logger:
    def __init__(self, logfile, loglevel):
        self.logfile = logfile
        self.loglevel = loglevel

    def setup_logger(self):
        """Setup the logger

        arguments:
        logfile  - file to log to, None for stdout
        loglevel - level to log in
        """
        f = '%(levelno)s\t%(lineno)d\t%(asctime)s\t%(message)s'
        loglevel = {'INFO': logging.INFO, 'DEBUG': logging.DEBUG}.get(
            self.loglevel, logging.WARNING)
        if self.logfile is None:
            logging.basicConfig(format=f, level=loglevel)
        else:
            logging.basicConfig(format=f, filename=self.logfile, level=self.loglevel)
        logging.debug('Logger initialized')

class Deck:
    def __init__(self, database, deckname):
        self.database = database
        self.deckname = deckname
        #print ("Database -> {}: {}".format(self.database, self.deckname))


    def get_db(self, database):
        """Helper function to start the database and initialize if necessary

        arguments:
        database - filepath for the sqlite databasae file

        returns: (sqlite-object, sqlite-cursor)
        """
        try:
            os.makedirs(os.path.dirname(database))
        except OSError as e:
            if e.errno != 17:
                raise e
        sq = sqlite3.connect(database)
        logging.debug('Connected with database at {}'.format(database))
        c = sq.cursor()
        q = 'CREATE TABLE IF NOT EXISTS decks (date TEXT, name TEXT UNIQUE)'
        logging.info('Creating decks table')
        logging.debug('With query: {}'.format(q))
        c.execute(q)
        return sq, sq.cursor()

    #@staticmethod
    def close_db(self,database):
        database.commit()
        database.close()


    def get_word_db(self, name):
        return '"words_{}"'.format(name)


    def get_stat_db(self, name):
        return '"stat_{}"'.format(name)


    def list_decks(self):
        """List the decks optionally with their entries

        arguments:
        database - filepath for the sqlite database file
        deckname - list of decknames to list. If empty all decks are listed.

        returns: [deck]
            where deck = {name, date_added, entries}
            where entries = [(a, b, times, times_correct, box)]
        """
        logging.info('list decks... with names: {}'.format(self.deckname))
        sq, c = self.get_db(self.database)
        decks = []
        q = 'SELECT rowid, name, date FROM decks'
        logging.info('getting deck information')
        logging.debug('with query: {}'.format(q))
        datenames = list(c.execute(q))
        for id_, name, date in datenames:
            if not self.deckname or name in self.deckname:
                decks.append({'name': name, 'date_added': float(date),
                              'entries': []})
                q = 'SELECT * FROM {}'.format(self.get_word_db(id_))
                logging.info('getting entries information')
                logging.debug('with query: {}'.format(q))
                for entry in c.execute(q):
                    decks[-1]['entries'].append(entry)
        self.close_db(sq)
        #self.close_db()
        return decks




    def remove_deck(self, deckname):
        """Remove a deck from the database

        arguments:
        database - filepath for the sqlite database file
        deckname - name of the deck to load in in

        returns: number of decks removed
        """
        logging.info('remove deck...')
        sq, c = self.get_db(self.database)
        q = 'SELECT rowid FROM decks WHERE name = ?'
        logging.info('finding matching tables')
        logging.info('with query: {}'.format(q))

        num = 0
        for (id_,) in list(c.execute(q, (deckname,))):
            q = 'DROP TABLE {}'.format(self.get_word_db(id_))
            logging.info('removing deck table: {}'.format(id_))
            logging.debug('with query: {}'.format(q))
            c.execute(q)
            q = 'DROP TABLE {}'.format(self.get_stat_db(id_))
            logging.info('removing statistics table: {}'.format(id_))
            logging.debug('with query: {}'.format(q))
            c.execute(q)
            q = 'DELETE FROM decks WHERE rowid={}'.format(id_)
            logging.info('removing deck entry: {}'.format(id_))
            logging.debug('with query: {}'.format(q))
            c.execute(q)
            num += 1
        sq.commit()
        sq.close()
        return num


    def export_deck(self, database, deckname):
        """Export a deck from the database

        arguments:
        database - filepath for the sqlite database file
        deckname - name of the deck to load in in

        yields: lines
        """
        logging.info('exporting deck...')
        sq, c = self.get_db(self.database)
        logging.info('getting deck information')
        #decks = self.list_decks(self.database, [deckname])
        decks = self.list_decks()
        if not decks:
            logging.warning('deck not found')
        else:
            for entry in decks[0]['entries']:
                if entry:
                    s = '{}\t{}\n'.format(entry[0], entry[1])
                    logging.debug('yielding: {}'.format(s))
                    yield s


    def load_from_file(self, lines):
        """Import a deck from a file

        arguments:
        lines    - generator for lines of input
        database - filepath for the sqlite database file
        deckname - name of the deck to load in in
        """
        logging.info('load Learning Words from file...')
        # todo
        # deck = Deck(database, deckname)
        sq, c = self.get_db(self.database)
        q = 'INSERT OR IGNORE INTO decks (date, name) values(?,?)'
        logging.info('inserting info in deck table')
        logging.debug('with query: {}'.format(q))
        c.execute(q, (time.time(), self.deckname))

        lastrowid = c.lastrowid
        dbname = self.get_word_db(lastrowid)
        q = 'CREATE TABLE IF NOT EXISTS {} (a TEXT, b TEXT,'\
            'times INTEGER, times_correct INTEGER, box INTEGER)'.format(dbname)
        logging.info('creating deck table')
        logging.debug('with query: {}'.format(q))
        c.execute(q)

        dbname2 = self.get_stat_db(lastrowid)
        q = ('CREATE TABLE IF NOT EXISTS {} (date INTEGER, correct INTEGER, '
             'grade TEXT, finished INTEGER)').format(dbname2)
        logging.info('creating statistics table')
        logging.debug('with query: {}'.format(q))
        c.execute(q)

        logging.info('inserting from {}'.format(lines))
        line_count = 1
        for line in lines:
            if line[0] != '#':
                # split on the first occurance  of ,
                splits = line.strip().split(',')
                #print("line {} is len {}".format(line_count, len(splits)))
                if len(splits) < 2:
                    logging.warning('line doesn\'t consist of two tab separated '
                                    'fields... Skipping')
                    continue
                if len(splits) > 2:
                    logging.warning(
                        'line has more columns... discarding extra columns...')
                q = ('INSERT OR IGNORE INTO {} (a, b, times, times_correct, box) '
                     'values(?,?,0,0,1)').format(dbname)
                #print ("adding entry {}".format( splits[:2]))
                logging.warning('inserting entry\nwith query: {}'.format(q))

                try:
                    c.execute(q, splits[:2])
                except sqlite3.Error as e:
                    print("SQL error encountered when fetching scan errors: " + e.args[0])

                line_count+=1
        sq.commit()
        sq.close()

class Session:
    def __init__(self, database, inverse, random, leitner, deckname):
        self.deck = Deck(database, deckname)
        self.sq, self.c = self.deck.get_db(database)
        self.entries = []
        self.cur = None
        #self.answer = ""
        if not inverse or random:
            leitner = 1

        q = 'SELECT rowid FROM decks WHERE name = ?'
        logging.info('finding deck with name: {}'.format(deckname))
        logging.debug('with query: {}'.format(q))
        deck = list(self.c.execute(q, (deckname,)))
        logging.info('found: {}'.format(deck))
        times = 0
        if not deck:
            logging.warning('No deck with that name')
            return
        else:
            rowid = deck[0][0]

        self.deckdb = self.deck.get_word_db(rowid)
        self.statdb = self.deck.get_stat_db(rowid)
        q = 'SELECT rowid, {}, times, times_correct, box FROM {}'.format(
            'b, a' if inverse else 'a, b', self.deckdb)
        if leitner:
            q += ' WHERE box = 0'
            for i in range(1, 5):
                if times % i == 0:
                    q += ' OR box = {}'.format(i)
        if random:
            logging.info('randomize questions...')
            q += ' ORDER BY Random()'
        logging.debug('with query: {}'.format(q))
        self.entries += list(self.c.execute(q))
        logging.debug('entries testing: {}'.format(self.entries))
        self.all_answers = len(self.entries)
        self.correct_answers = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.entries:
            self.cur = self.entries.pop(0)
            return self.cur[1]
        else:
            logging.info('no entries left, writing stats')
            raise StopIteration

    def answer_current(self, answer):
        if self.cur is None:
            logging.info('Nothing to be answered, nothing has been asked')
        #print ("self.cur {}:{}".format(self.cur[1], self.cur[2]))
        self.answer = self.cur[2]
        #logging.info('comparing "{}" with "{}"'.format(answer, self.answer))


        correct = False
        #answer == self.answer
        #print ("answer provided {}".format(self.answer))

        if answer == 'checking':
            return
        elif answer == 'correct':
            p = (self.cur[3]+1, self.cur[4]+1,
                 min(self.cur[5]+1, LEITNER_BOXES), self.cur[0])
            self.correct_answers += 1
            print("Pass")
            correct = True
        else:
            print("Fail")
            p = (self.cur[3]+1, self.cur[4],
                 max(self.cur[5]-1, 0), self.cur[0])
            correct = False

        #logging.info('updating word')
        q = 'UPDATE {} SET times=?, times_correct=?, box=? WHERE rowid=?'.\
            format(self.deckdb)
        logging.debug('with query: {}'.format(q))
        self.c.execute(q, p)
        #self.cur = None
        return correct

    def write_stats(self, total=True):
        logging.debug('writing statistics')
        mark = float((self.correct_answers/float(self.all_answers))*100.0)
        logging.debug('closing db')
        q = ('INSERT OR IGNORE INTO {} (date, correct, grade, finished) '
             'values(?,?,?,?)').format(self.statdb)
        logging.info('added statistics row in deck table')
        logging.debug('with query: {}'.format(q))
        self.c.execute(q, (time.time(), self.correct_answers, str(mark),
                           1 if total else 0))
        self.deck.close_db(self.sq)
        return mark


def start_learning (session):

    #os.system('clear')
    try:
        #print (dir(session))
        for s in session:
            os.system('clear')

            #answer = ""
            print ("###### Front2-side #########")
            for i in range(0,2):
                print('#')
            print ("# {}: ".format(s))
            for i in range(0,2):
                print('#')
            print ("###### Flip-side #########")

            for i in range(0,2):
                print('#')
            answer = 'checking'
            session.answer_current(answer)
            print ("# {}: ".format(session.answer))
            for i in range(0,2):
                print('#')
            print ("#######################")
            print("# ((P)ass|(F)ail|(S)kip)|(D)elete|(E)dit|(Q)uit)", flush=True, end = '')
            passFailAbort = readchar.readchar()
            #print (resp)
            #key = readchar.readkey()
            #passFailAbort=input("# ((P)ass|(F)ail|(S)kip)|(D)elete|(E)dit)")
            if passFailAbort.lower()== 'p':
                answer = 'correct'

            elif passFailAbort.lower()== 'f':
                answer = 'fail'

            elif passFailAbort.lower()== 'd':
                answer = 'delete'
            elif passFailAbort.lower()== 's':
                answer = 'skip'
            elif passFailAbort.lower()== 'e':
                ## TODO:
                ## add edit support
                answer = 'edit'
            elif passFailAbort.lower()== 'q':
                ## TODO:
                ## quit
                stats = session.write_stats(False)
                #print ("Exiting")
                print('\nFinished\n\nGrade: {}'.format(stats))
                return
                #answer = 'edit'
            if session.answer_current(answer):
                print('correct!')
            else:
                print('incorrect, it had to be: "{}"'.format(session.answer))
        print ("# {}: ".format(session.answer))
        stats = session.write_stats()
    except KeyboardInterrupt:
        stats = session.write_stats(False)
    print('\nFinished\n\nGrade: {}'.format(stats))


def session(database, deckname, inverse, random, leitner):
    """Start a session

    arguments:
    database - filepath for the sqlite database file
    deckname - name of the deck to list, if None all decks are shown
    inverse  - flag for inversing question and answer
    random   - flag for randomizing questions
    leitner  - flag for using leitner system.

    returns: Session object
    """
    logging.info('starting session')
    return Session(database, inverse, random, leitner, deckname)
