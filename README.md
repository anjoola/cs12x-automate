CS 121 Automation Tool
======================

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
folder of the form `<username>-<assignment name>`. Any resource files should
be in the assignment's base directory.

After the repository is cloned, it should have the directory structure
detailed above, except the `assignments` folder needs to be filled in with
the correct specs and student files!

Running
-------

    python main.py --assignment <assignment name>
                   [--files <files to grade>]
                   [--students <students to grade>]
                   [--after <grade files submitted after YYYY-MM-DD>]
                   [--user <database username>]
                   [--db <database to use for grading>]
                   [--deps] [--purge]

Use `--purge` if the entire database is to be purged prior to grading. This
should be used between assignments and if there were any errors in grading
prior to this.

The `--deps` flag is used to run the dependencies for the assignment.
Dependencies are usually SQL files that create the tables and rows necessary
for testing. They should only be run once per assignment unless `--purge` is
used.

Example usage:

    python main.py --assignment cs121hw3 --files queries.sql
                   --students agong mqian

Or:

    python main.py --assignment cs121hw7 --after 2014-03-01

Output
------
Results of the grading run are outputted in the `_results/` folder of the
directory structure:

    |-- assignments/
        |-- cs121hw2/
            |-- _results/
                |-- files
                |-- style
                |-- index.html
            |-- students/
            |-- cs121hw2.spec

The output can be viewed in the `index.html` file, which opens up a web view.
The `files` folder contains all the files necessary for this web view, and
`style` contains the Javascript and CSS.
