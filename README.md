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

## Contents copy

1. copy audio contents from local pc `$ scp -r /mnt/h/kick-preview/audio/* raspberrypi:/home/quark/Work/my-kick-preview-db/contents/audio/`
1. copy image contents from local pc `$ scp -r /mnt/h/kick-preview/image/* raspberrypi:/home/quark/Work/my-kick-preview-db/contents/image/`

### DBに新しいデータを挿入

- 一括送信してくれるやつ

1. import.csvに上記コマンドの為のデータ入れる
2. `rye run python batch_uploader.py`でimport.csvのデータを一括挿入

