# beansorter
View coffee shops in your area - project for University of Helsinki database lab

Beansorter is a web application that allows you to find and filter coffee shops around you. Always find an open cafe.

## Features

- Beansorter displays a list of coffee shops
- Results can be searched
- Registered users can add new coffee shops to the database, post written reviews, and select from keyword "tags"
- Admin users can moderate both venue entries and reviews
- Admin users can create new keywords to filter results by

### Cut features
I had originally planned to display results on a map, but that was discarded due to time constraints. Also cut: ability to filter search results by opening hours/tags.

## Get started

An instance is available at [beansorter.fly.io](https://beansorter.fly.io). There is an admin user to test admin features: username ````admin````, password ````tsohalabra````.

You can also launch a beansorter instance locally:

1. Create .env, containing
    
        SECRET_KEY=<secret>
        DATABASE_URL=<pointing to a postgres:// instance>

2. Activate venv and install dependencies

        python3 -m venv venv
        source venv/bin/activate
        pip install -r ./requirements.txt

3. Utilise schema

        psql < schema.sql

4. Now start the instance

        flask run

5. After creating a user in the web app, make yourself admin

        $ psql
        => UPDATE users SET role=1 WHERE name='<your username here>'
        => \q