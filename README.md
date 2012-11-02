rhythmbox-gmusic-sync
=====================

Plugin to sync metadata from Rhythmbox to Google Music

**Planned features**
Send metadata from Rhythmbox to Google Music when
* Rating changes
* Title changes
* Artist changes
* Album changes

And if possible
* Song deleted

Preferences window for username, password


**Planned flow**
On plugin activate, use GMusic API to get_all_songs.  Subscribe to signal 'playing-song-property-changed'. 
When invoked, match API, set ["rating"] or ["property"].  Then .change_song_metadata(songEntry). 
