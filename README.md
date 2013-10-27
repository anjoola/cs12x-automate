cs12x-automate
==============

Folder Structure
----------------
All files for a particular assignment should be in that assignments folder. For example,
for assignment `cs121hw3`, the directory structure is:

    main.py
    style.py
    |-- cs121hw3
        |-- cs121hw3.spec
        |-- make-banking.sql
        |-- make-grades.sql
        |-- test-dates.sql
        |-- agong-cs121hw3
            |-- queries.sql
            |-- make-auto.sql
        |-- mqian-cs121hw3
            |-- queries.sql
            |-- make-auto.sql

The specifications for the assignment must be in a file called `<assignment name>.spec`.
Each student's submission should be in a separate folder of the form `<username>-<assignment name>`.

Running
-------

    python main.py --assignment <assignment name> [--files <files to grade>] [--students <students to grade>]

For example:

    python main.py --assignment cs121hw3 --files queries.sql --students agong mqian

Tools
-----
* [MySQL connector for Python](http://dev.mysql.com/downloads/connector/python/)
* [SQL Parser](https://code.google.com/p/python-sqlparse/)
* [prettytable](https://code.google.com/p/prettytable/)
* Python 2.6+
