# Contents Requirement

You will be required to create the following `.json` files.

__anilist.json__:

Example configuration file containing your userId, userName for anilist, which will be used for list comparisons.
```json
{
    "userId": 80546,
    "userName": "wax911",
    "type": "ANIME",
    "statusIn": ["CURRENT","PLANNING","COMPLETED","PAUSED","DROPPED","REPEATING"],
    "forceSingleCompletedList": true,
    "sort": "MEDIA_ID"
}
```
> Please see the query file: `../query/media_collection.graphql` if you want to know where each of the above paramters will be used

__app.json__:

Example configuration file for the application which sets the monitored directory where torrents should be copied to.
the `torrent_download_directory` indicates where torrent files are saved during download for this app and finally
`torrent_queued_postfix` is an the postfix filename that will be appended to .torrent files when they've been added.
```json
{
  "torrent_monitor_directory": "/media/PopStore/Downloads/Torrents/Source/",
  "torrent_download_directory": "./torrents/",
  "torrent_preferred_quality": "[720p]",
  "torrent_preferred_group": "[HorribleSubs]",
  "torrent_queued_postfix": ".added",
  "torrent_keep_file_after_queuing": true
}
```

__plex.json__:

Example configuration file containg your media server section information, in this case my library where anime shows can be found is called `Anime` which is a library type of `Shows`
```json
{
  "section_library_name": "Anime",
  "section_library_type": "Shows"
}
```