# Setup

## DB

1. install [mariaDB](https://mariadb.org/)
2. start mariadb `$ sudo systemctl start mariadb`
3. check `$ sudo mariadb`
4. create user `MariaDB [(none)]> GRANT ALL ON *.* TO 'quark'@'localhost' IDENTIFIED BY 'mariadmin' WITH GRANT OPTION;`
5. create database `MariaDB [(none)]> CREATE DATABASE kick_preview;`
6. create table `$ mysql -u quark -p kick_preview < tracks_create_table.sql`

## DB API

1. install [rye](https://rye.astral.sh/)
2. run `$ rye sync`
3. run `rye run python api.py`
