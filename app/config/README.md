# Contents Requirement

You will be required to create the following `.json` files.

__anilist.json__:

Configuration file containing your userId, userName for anilist, which will be used for list comparisons.
```json
{
    "userId": 10,
    "userName": "user23",
    "type": "ANIME",
    "statusIn": ["CURRENT","PLANNING","COMPLETED","PAUSED","DROPPED","REPEATING"],
    "forceSingleCompletedList": true,
    "sort": "MEDIA_ID"
}
```

__app.json__:

Configuration file for the application which sets the monitored directory where torrents should be copied to.
the `torrent_download_directory` indicates where torrent files are saved during download for this app and finally
`torrent_queued_postfix` is an the postfix filename that will be appended to .torrent files when they've been added.
```json
{
  "torrent_monitor_directory": "~Downloads/Torrents/Source/",
  "torrent_download_directory": "./torrents/",
  "torrent_preferred_group": "[HorribleSubs]",
  "torrent_queued_postfix": ".added",
  "torrent_file_move_after_download": false
}
```