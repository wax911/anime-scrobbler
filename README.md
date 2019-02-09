# Anime Scrobbler

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

### [Pickle DB](https://github.com/patx/pickledb)

> pickleDB is lightweight, fast, and simple database based on the
[json](https://docs.python.org/3/library/json.html) module.
And it's BSD licensed!

```python
import pickledb

db = pickledb.load('test.db', False)

db.set('key', 'value')

db.get('key')

db.dump()
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
