cs12x-automate
==============

Libraries
---------
The following tools and libraries must be installed prior to running the tool.
* [Python 2.6+](https://www.python.org/download/)
* [Python MySQL Connector](http://dev.mysql.com/downloads/connector/python/)
* [SQL Parser](https://code.google.com/p/python-sqlparse/)
* [prettytable](https://code.google.com/p/prettytable/)


Directory Structure
-------------------
The directory structure of the automation tool is as follows. All files for a
particular assignment should be in the corresponding folder (for example, the
`cs121hw2/` folder listed below).

    |-- assignments/
        |-- cs121hw2/
            |-- students/
                |-- agong-cs121hw2/
                |-- mqian-cs121hw2/
            |-- cs121hw2.spec
            |-- make-banking.sql
            |-- make-library.sql
            |-- make-university.sql
        |-- cs121hw3
    |-- src/
        |-- *.py
    |-- style/

The specifications for the assignment must be in a file called
`<assignment name>.spec`. Each student's submission should be in a separate
folder of the form `<username>-<assignment name>`.

Running
-------

    python main.py --assignment <assignment name>
                   [--files <files to grade>]
                   [--students <students to grade>]
                   [--after <grade files submitted after this YYYY-MM-DD>]
                   [--user <database username>]
                   [--db <database to use for grading>]
                   [--deps] [--purge]

Use `--purge` if the entire database is to be purged prior to grading.

Here, `--deps` is used if the dependencies for the assignment are to be run.
Dependencies are usually SQL files that create the tables and rows necessary
for testing. They should only be run once per assignment unless `--purge` is
used.

For example:

    python main.py --assignment cs121hw3 --files queries.sql
                   --students agong mqian

Or:

    python main.py --assignment cs121hw7 --after 2014-03-01

Output
------
TODO
md or HTML format


