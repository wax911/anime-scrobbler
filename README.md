# Anime Scrobbler (_for research purposes of course_)

Just an automation utility for fun, ~~potentially useless?~~  to download missing shows from 
your [AniList](https://anilist.co) collection not present in a plex media server.

## Dependencies

### [Nyaa API](https://github.com/JuanjoSalvador/NyaaPy)

> keyword     |  String  |  Keyword for the search query
> category    |  Integer | See [Categories](https://github.com/JuanjoSalvador/NyaaPy/wiki/Categories-and-subcategories)
> subcategory | Integer  | See [Categories](https://github.com/JuanjoSalvador/NyaaPy/wiki/Categories-and-subcategories)
> filters     |  Integer | See [Filters](https://github.com/JuanjoSalvador/NyaaPy/wiki/Docs-for-Nyaa.si)
> page        |  Integer | Number between 0 and 1000

```python
Nyaa.search(keyword="Shoukoku no Altair", category=1)
```

> Returns a list of dictionaries like this
```json
{
    'category': "Anime - English-translated",
    'url': "https://nyaa.si/view/968600",
    'name': "[HorribleSubs] Shoukoku no Altair - 14 [720p].mkv",
    'download_url': "https://nyaa.si/download/968600.torrent",
    'magnet': <magnet torrent URI>
    'size': "317.2 MiB",
    'date': "2017-10-13 20:16",
    'seeders': "538",
    'leechers': "286",
    'completed_downloads': "852"
}
```

### [TinyDB](https://github.com/msiemens/tinydb)

> TinyDB is a lightweight document oriented database optimized for your happiness :) 
It's written in pure Python and has no external dependencies. The target are small apps 
that would be blown away by a SQL-DB or an external database server.

#### Example Code

```python
from tinydb import TinyDB
db = TinyDB('/path/to/db.json')
db.insert({'int': 1, 'char': 'a'})
db.insert({'int': 1, 'char': 'b'})
```

__Query Language__

```python
from tinydb import TinyDB, Query

User = Query()
db = TinyDB('/path/to/db.json')
# Search for a field value
db.search(User.name == 'John')
[{'name': 'John', 'age': 22}, {'name': 'John', 'age': 37}]

# Combine two queries with logical and
db.search((User.name == 'John') & (User.age <= 30))
[{'name': 'John', 'age': 22}]

# Combine two queries with logical or
db.search((User.name == 'John') | (User.name == 'Bob'))
[{'name': 'John', 'age': 22}, {'name': 'John', 'age': 37}, {'name': 'Bob', 'age': 42}]

# More possible comparisons:  !=  <  >  <=  >=
# More possible checks: where(...).matches(regex), where(...).test(your_test_func)
```

__Tables__

```python
table = db.table('name')
table.insert({'value': True})
table.all()
[{'value': True}]
```

### [Plex API](https://github.com/pkkid/python-plexapi)

> There are two types of authentication. If you are running on a separate 
network or using Plex Users you can log into MyPlex to get a PlexServer instance. 
An example of this is below. NOTE: Servername below is the name of the server 
(not the hostname and port). 
If logged into Plex Web you can see the server name in the top left above your available libraries.

```python
from plexapi.myplex import MyPlexAccount

account = MyPlexAccount('<USERNAME>', '<PASSWORD>')  
# returns a PlexServer instance
plex = account.resource('<SERVERNAME>').connect()
```
> If you want to avoid logging into MyPlex and you already know your auth token string, 
you can use the PlexServer object directly as above, but passing in the baseurl and auth token directly.

```python
from plexapi.server import PlexServer

baseurl = 'http://plexserver:32400'
token = '2ffLuB84dqLswk9skLos'
plex = PlexServer(baseurl, token)
```

> [Usage examples](https://github.com/pkkid/python-plexapi)

### [GraphQL](https://github.com/graphql-python/gql)

> The example below shows how you can execute queries against a local schema.

```python
from gql import gql, Client

client = Client(schema=schema)
query = gql('''
{
  hello
}
''')

client.execute(query)
```

### [Dacite](https://github.com/konradhalas/dacite)

> This module simplifies creation of data classes ([PEP 557][pep-557])
from dictionaries.

```python
from dataclasses import dataclass
from dacite import from_dict


@dataclass
class User:
    name: str
    age: int
    is_active: bool


data = {
    'name': 'john',
    'age': 30,
    'is_active': True,
}

user = from_dict(data_class=User, data=data)

assert user == User(name='john', age=30, is_active=True)
```

### [anitopy](https://github.com/igorcmoura/anitopy)

> Anitopy is a Python library for parsing anime video filenames. It's simple to use and it's based on the C++ library `Anitomy <https://github.com/erengy/anitomy>`_.

```python
import anitopy
anitopy.parse('[TaigaSubs]_Toradora!_(2008)_-_01v2_-_Tiger_and_Dragon_[1280x720_H.264_FLAC][1234ABCD].mkv')
```

> Will result in the following:
```json
{
    'anime_title': 'Toradora!',
    'anime_year': '2008',
    'audio_term': 'FLAC',
    'episode_number': '01',
    'episode_title': 'Tiger and Dragon',
    'file_checksum': '1234ABCD',
    'file_extension': 'mkv',
    'file_name': '[TaigaSubs]_Toradora!_(2008)_-_01v2_-_Tiger_and_Dragon_[1280x720_H.264_FLAC][1234ABCD].mkv',
    'release_group': 'TaigaSubs',
    'release_version': '2',
    'video_resolution': '1280x720',
    'video_term': 'H.264'
}
```

### [Unidecode](https://pypi.org/project/Unidecode/)

> The module exports a function that takes an Unicode object (Python 2.x) or string (Python 3.x) and returns a string (that can be encoded to ASCII bytes in Python 3.x):

```python
from unidecode import unidecode
unidecode(u'ko\u017eu\u0161\u010dek')
# outputs > 'kozuscek'
unidecode(u'30 \U0001d5c4\U0001d5c6/\U0001d5c1')
# outputs > '30 km/h'
unidecode(u"\u5317\u4EB0")
# outputs > 'Bei Jing '
```