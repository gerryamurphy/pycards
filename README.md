# pycards 0.3

### Introduction
*pycards* is an engine with different frontends to memorize things using
[flashcards][1]. *pycards* is written in [Python 3][2] and uses a [sqlite][3]
database to store all the data. It is starting to get a little usable.

### Usage of `cli.py`: Command line interface
`cli.py [globaloptions] {list,load,remove,export,session} [options] [args]`

- `globaloptions`
	- `-h`, `--help`
	
		Show the help message and exit
	- `-d DATABASE`, `--database DATABASE`
	
		Specify a custom database file. Default: `~/.pycards/pycards.db`
	- `-l {INFO,DEBUG,SILENT}`, `--loglevel {INFO,DEBUG,SILENT}`
	
	  Specify a custom log level. Default: `SILENT`
	- `-f LOGFILE`, `--logfile LOGFILE`
	
	  Specify a log file location. Default: stdout
	- `--version`
	
		Show version number and exit
- `list`: `cli.py [globaloptions] list [options] [deckname]`
	- `-h`, `--help`
	
		Show the `list` specific help message and exit
	- `-e`, `--show-entries`
	
		Flag to print all the individual entries
	
	- `deckname`
	
		Name of the deck to print. If not given, all decks will be printed
- `load`:  `cli.py [globaloptions] load [options] deckname [filepath]`
	- `-h`, `--help`
	
		Show the `load` specific help message and exit
	- `-e ENCODING`, `--encoding ENCODING`
	
		Encoding to read the file/stream in
	
	- `deckname`
	
		Name of the deck to load the entries in
	- `filepath`
	
		Filepath to load the entries from. If not given stdin is used
- `remove`: `cli.py [globaloptions] remove [options] deckname`
	- `-h`, `--help`
	
		Show the `remove` specific help message and exit
	- `deckname`
	
		Name of the deck to remove
- `export`:  `cli.py [globaloptions] export [options] deckname [filepath]`
	- `-h`, `--help`
	
		Show the `export` specific help message and exit
	- `deckname`
	
		Name of the deck to export
	- `filepath`
	
		Location to export to. If not given stdout is used
- `session`: `cli.py [globaloptions] session [options] deckname`
	- `-h`, `--help`
	
		Show the `session` specific help message and exit
	- `-l`, `--leitner`
	
		Use the [leitner system][4]
	- `-r`, `--random`
	
		Randomize the questions
	- `-i`, `--inverse`
	
		Inverse the question and the answer
	- `deckname`
	
		Name of the deck to start the session with

### TODO, in order of importance
- Web interface
- Curses interface
- Graphical user interface

### Changelog
*[Version 0.3](https://github.com/dopefishh/pycards/releases/tag/v0.3)*
- [Leitner][4] system implemented.
- Changed systems so that the system is with flags instead of names. In this
  way one can do random-leitner-inverse for example.
- All queries parameterized where possible, also changed deck databases to be
  consisting of ids and ascii only to let names contain every character.
- Updated readme with help.

*[Version 0.2](https://github.com/dopefishh/pycards/releases/tag/v0.2)*
- List deck(s) either with or without all the entries.
- Remove a deck.
- Export to a file.
- Load a deck from tab separated files with two columns.
- Play a session with a deck and different systems: ordered, random.

*[Version 0.1](https://github.com/dopefishh/pycards/releases/tag/v0.1)*
- Initial version

### LICENCE
See `LICENCE` file.

[1]: https://en.wikipedia.org/wiki/Flashcard
[2]: https://www.python.org
[3]: https://www.sqlite.org
[4]: https://en.wikipedia.org/wiki/Leitner_system
