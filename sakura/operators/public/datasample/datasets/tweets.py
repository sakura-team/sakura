#!/usr/bin/env python
from sakura.daemon.processing.stream import SimpleStream
TWEETS = (
    ("Vincent" , 2.5, 48.8, "Tata", "2016-12-23"),
    ("Paul", 2.4, 48.9, "Toto", "2017-2-12"),
    ("Hariz", 2.3 ,48.3, "Tictic Aujourd'hui est une longue journée -- Hariz", "2016-12-12"),
    ("Nabil",  2.3 ,48.5, "Tete", "2017-3-21")
)

def compute():
    for row in TWEETS:
        yield row

# dataset description
STREAM = SimpleStream('Tweets', compute)
STREAM.add_column("Actor", (str, 16))
STREAM.add_column("Longtitude", float)
STREAM.add_column("Latitude", float)
STREAM.add_column("Text", (str, 140))
STREAM.add_column("Date", (str, 12))
STREAM.length = len(TWEETS)
