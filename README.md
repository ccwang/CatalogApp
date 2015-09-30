# Item Catalog App

## Introduction

This project is to develop a web application that provides a list of 
items within a variety of categories and integrate google user registration
and authentication. Authenticated users can add, edit and delete their
own items.

## What's is included

```
project3_catalog
├──README.md
├──database_setup.py
├──database_init.py
├──application.py
├──client_secrets.json
├──catalog.db
├──templates
    ├──catalog_latest.html
    ├──catalog_category.html
    ├──catalog_description.html
    ├──main.html
    ├──login.html
    ├──add.html
    ├──edit.html
    ├──delete.html
├──static
    ├──styles.css
```

## How to use

**Create the `tournament` database**

```
vagrant@vagrant-ubuntu-trusty-32:/vagrant/tournament$ psql
psql (9.3.9)
Type "help" for help.

vagrant=> \i tournament.sql
DROP DATABASE
CREATE DATABASE
You are now connected to database "tournament" as user "vagrant".
CREATE TABLE
CREATE TABLE
CREATE VIEW
CREATE VIEW
CREATE VIEW
tournament=> \q
```

**Run Test**

```
vagrant@vagrant-ubuntu-trusty-32:/vagrant/tournament$ python tournament_test.py
1. Old matches can be deleted.
2. Player records can be deleted.
3. After deleting, countPlayers() returns zero.
4. After registering a player, countPlayers() returns 1.
5. Players can be registered and deleted.
6. Newly registered players appear in the standings with no matches.
7. After a match, players have updated standings.
8. After one match, players with one win are paired.
Success!  All tests pass!

```
