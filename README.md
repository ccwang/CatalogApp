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

**Create the `catalog` database**

```
rm catalog.db
python database_init.py
```

**Run Server**

```
python application.py
```

**Open the website**

http://localhost:8000/

You can explore the website by logging in with google account.

**The JSON can be accessed from **

http://localhost:8000/catalog.json