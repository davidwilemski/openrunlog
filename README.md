#Open Run Log

[![Build Status](https://travis-ci.org/davidwilemski/openrunlog.png?branch=master)](https://travis-ci.org/davidwilemski/openrunlog) [![Requirements Status](https://requires.io/github/davidwilemski/openrunlog/requirements.png?branch=master)](https://requires.io/github/davidwilemski/openrunlog/requirements/?branch=master)


## What is Open Run Log?
I intend for Open Run Log (ORL) to be an open source platform 
that allows people to easily and quickly record their runs and additionally
view information about past workouts easily in a visual manner. 

I aim to do away with tedious spreadsheets and other solutions that end
up being a huge hassle once you have any sort of volume.

## Running ORL
If you'd like to your own copy of ORL either for development or just
personal use you can follow these simple steps.

First, some dependencies:

- MongoDB 
- redis
- Python (I use 2.7 but 2.6 *should* work as well)

Steps:

1) Install the required Python modules (virtualenv recommended)

`pip install -r requirements.txt`

2) Configure via environment variables

```
export ORL_DB_NAME="openrunlog"
export ORL_DB_URI="mongodb://localhost/openrunlog"
export ORL_DEBUG="True"
export ORL_COOKIE_SECRET="insertyourrandomstringhere"
```

3) Run ORL!

`supervisord`
