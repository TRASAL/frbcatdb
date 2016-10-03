# frbcatdb

Database for storing the FRB catalogue. This DB contains old FRB events and will
also contain new FRBs as detected by the AA-ALERT FRB detection pipeline from Apertif
observations.

create_db.sql can be used to create an empty DB with the schema tables.

load_db.csh (which uses dump_db.dat) loads a backup of the DB. For this, first create a empty DB (without the schema tables), i.e.:

```
$bash>  mysql -u <user> --password=<password>
$mysql> create database frbcat;
$mysql> exit;
$bash>  ./load_db.csh
```

db.architect contains a Entity-Relationship diagram of the DB and can be opened and edited with SQL Power Architect (http://www.sqlpower.ca/page/architect).

![FRB Catalogue ER diagram](db.architect.pdf)
