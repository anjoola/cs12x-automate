cs12x-automate
==============

Folder Structure
----------------
All files for a particular assignment should be in that assignments folder. For example,
for assignment `cs121hw3`, the directory structure is:

    main.py
    *.py
    style/

    |-- cs121hw3/
        |-- _results/
            |-- _files/
                |-- agong-queries.sql.html
                |-- agong-other.sql.html
            |-- style/
                |-- javascript.js
                |-- css.css
        |-- students/
            |-- agong-cs121hw3
            |-- mqian-cs121hw3

        |-- cs121hw3.spec
        |-- make-banking.sql
        |-- make-grades.sql
        |-- test-dates.sql

The specifications for the assignment must be in a file called `<assignment name>.spec`.
Each student's submission should be in a separate folder of the form `<username>-<assignment name>`.

Running
-------

    python main.py --assignment <assignment name>
                   [--files <files to grade>]
                   [--students <students to grade>]
                   [--after <grade students whose submission is on or after this student's>]

For example:

    python main.py --assignment cs121hw3 --files queries.sql
                   --students agong mqian

Or:

    python main.py --assignment cs121hw7 --after agong
    

Output
------
TODO
md or HTML format


Tools
-----
* [MySQL connector for Python](http://dev.mysql.com/downloads/connector/python/)
* [SQL Parser](https://code.google.com/p/python-sqlparse/)
* [prettytable](https://code.google.com/p/prettytable/)
* Python 2.6+
