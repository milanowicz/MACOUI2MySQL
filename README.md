MACOUI2MySQL
============

This Python script download Organizationally Unique Identifier assigned by the IEEE vendor ID from the website and import it into the database or update them.


Requirements
============

* Linux
* Python 2.7
* MySQL
* Cron


Installation
============

* Create the MySQL table with the CreateTable.sql script
* Alters the values in the Python script to yours
* Add a new cron job for the python script
* $ crontab -e
*   0 3 * * 0 python MACOUI2MySQL.py


