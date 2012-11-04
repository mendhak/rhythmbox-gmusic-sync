from gi.repository import GObject, Peas, RB, Gio
import threading
from gmusicsyncconfig import GMusicSyncConfigDialog
from gmusicapi.api import Api

class GMusicSync(GObject.Object, Peas.Activatable):

    proc = None
    __gtype_name = 'GMusicSync'
    object = GObject.property(type=GObject.Object)

    def do_activate(self):
        self.enabled = True
        t = self.GMusicAPIThread(self.setup_listeners)
        t.start()


    class GMusicAPIThread(threading.Thread):
        def __init__(self, cb):
            threading.Thread.__init__(self)
            self.callback = cb

        def run(self):
            api = Api()

            #TODO: Handle the case of a GSettings schema not existing and warning the user.
            settings = Gio.Settings("org.gnome.rhythmbox.plugins.gmusicsync")
            username = settings['username']
            password = settings['password']

            if len(username) == 0 or len(password) == 0:
                print "Credentials not supplied, cannot get information from Google Music"
            else:

                logged_in = False
                attempts = 0

                while not logged_in and attempts < 3:
                    logged_in = api.login(username, password)
                    attempts += 1

                if not api.is_authenticated():
                    print "Could not log in to Google Music with the supplied credentials."
                else:
                    print "Logged in to Google Music"

            self.callback(api)


    def setup_listeners(self, api):
        self.db = self.object.props.db
        self.sp = self.object.props.shell_player

        #Get list of songs from Google Music
        self.api = api

        if not self.api.is_authenticated():
            return

        self.allSongs = self.api.get_all_songs()
        print "%s songs retrieved from Google Music" % len(self.allSongs)

        self.db_entry_ids = (self.db.connect('entry-changed', self.entry_changed),
                             self.db.connect('entry-deleted', self.entry_deleted))

        self.player_cb_ids = (  self.sp.connect('playing-song-changed', self.playing_entry_changed),)


    def playing_entry_changed (self, sp, entry):

        if not entry or not self.enabled:
            return

        different = False

        song = self.find_song(
            entry.get_string(RB.RhythmDBPropType.TITLE),
            entry.get_string(RB.RhythmDBPropType.ARTIST),
            entry.get_string(RB.RhythmDBPropType.ALBUM),
            entry.get_string(RB.RhythmDBPropType.GENRE))

        if not song:
            return

        if song['artist'].encode('utf8').lower() != entry.get_string(RB.RhythmDBPropType.ARTIST).lower():
            different = True
            song['artist'] = entry.get_string(RB.RhythmDBPropType.ARTIST)

        if song['album'].encode('utf8').lower() != entry.get_string(RB.RhythmDBPropType.ALBUM).lower():
            different = True
            song['album'] = entry.get_string(RB.RhythmDBPropType.ALBUM)

        if song['genre'].encode('utf8').lower() != entry.get_string(RB.RhythmDBPropType.GENRE).lower():
            different = True
            song['genre'] = entry.get_string(RB.RhythmDBPropType.GENRE)

        if int(entry.get_double(RB.RhythmDBPropType.RATING)) != int(song['rating']):
            different = True
            song['rating'] = int(entry.get_double(RB.RhythmDBPropType.RATING))

        if different and self.api.is_authenticated():
            self.api.change_song_metadata(song)


    def entry_deleted(self, entry, user_data):
        #Not deleted off disk, just removed from the player
        if not self.enabled:
            return

    def entry_changed(self, db, entry, changes):
        if not self.enabled:
            return

        currentTitle = entry.get_string(RB.RhythmDBPropType.TITLE)
        currentAlbum = entry.get_string(RB.RhythmDBPropType.ALBUM)
        currentArtist = entry.get_string(RB.RhythmDBPropType.ARTIST)
        currentGenre = entry.get_string(RB.RhythmDBPropType.GENRE)


        for i in range(0,changes.n_values):
            change = changes.get_nth(i)
            song = None

            if change.prop is RB.RhythmDBPropType.ALBUM:
                print "Album changed from %s to %s" % (change.old, change.new)
                song = self.find_song(currentTitle, currentArtist, change.old, currentGenre)
                if song: song['album'] = change.new
            if change.prop is RB.RhythmDBPropType.ARTIST:
                print "Artist was changed from %s to %s" % (change.old, change.new)
                song = self.find_song(currentTitle, change.old, currentAlbum, currentGenre)
                if song: song['artist'] = change.new
            if change.prop is RB.RhythmDBPropType.RATING:
                print "Assigned a rating of %s" % change.new
                song = self.find_song(currentTitle, currentArtist, currentAlbum, currentGenre)
                if song: song['rating'] = change.new
            if change.prop is RB.RhythmDBPropType.GENRE:
                print "New genre assigned is %s" % change.new
                song = self.find_song(currentTitle, currentArtist, currentAlbum, change.old)
                if song: song['genre'] = change.new
            if change.prop is RB.RhythmDBPropType.TITLE:
                print "Title changed from %s to %s" % (change.old, change.new)
                song = self.find_song(change.old, currentArtist, currentAlbum, currentGenre)
                if song: song['name'] = change.new

            if song and self.api.is_authenticated():
                self.api.change_song_metadata(song)

            #Special case: delete
            #TODO: Make this a checkbox in settings screen
            if change.prop is RB.RhythmDBPropType.HIDDEN:
                print "Song %s was deleted from disk" % entry.get_string(RB.RhythmDBPropType.TITLE)
                song = self.find_song(currentTitle, currentArtist, currentAlbum, currentGenre)
                if song and self.api.is_authenticated():
                    self.api.delete_songs(song["id"])


    def find_song(self, title, artist=None, album=None, genre=None):

        found = []

        for song in self.allSongs:
            if song['name'].encode('utf8').lower() == title.lower():
                found.append(song)

        if len(found) > 1 and artist:
            for song in found:
                if not song['artist'].encode('utf8').lower() == artist.lower():
                    found.remove(song)

        if len(found) > 1 and album:
            for song in found:
                if not song['album'].encode('utf8').lower() == album.lower():
                    found.remove(song)

        if len(found) > 1 and genre:
            for song in found:
                if not song['genre'].encode('utf8').lower() == genre.lower():
                    found.remove(song)

        if len(found) == 0:
            return None

        return found[0]


    def do_deactivate(self):
        if not self.api is None:
            self.api.logout()
            self.enabled = False


