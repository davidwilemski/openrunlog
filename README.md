#Open Run Log

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
- Python (I use 2.7 but 2.6 *should* work as well)

Steps:

1) Install the required Python modules (virtualenv recommended)

`pip install -r requirements.txt`

2) Make a copy of the example config file and enter all correct values:

`cd app`

`cp orl_settings.example.py orl_settings.py`

(now open with your favorite editor and add all the info)

3) Run ORL!

`cd app`

`python main.py <port_number>`
