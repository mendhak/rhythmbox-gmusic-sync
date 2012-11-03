from gi.repository import GObject, Peas, RB, Gio
import threading
from gmusicsyncconfig import GMusicSyncConfigDialog
from gmusicapi.api import Api

class GMusicSync(GObject.Object, Peas.Activatable):
    """
    This is an 'empty' Rhythmbox plugin which invokes another Python script to control Rhythmbox.
    """

    proc = None
    __gtype_name = 'GMusicSync'
    object = GObject.property(type=GObject.Object)

    def do_activate(self):
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
        db = self.object.props.db

        #Get list of songs from Google Music
        self.api = api

        if not self.api.is_authenticated():
            return

        self.allSongs = self.api.get_all_songs()
        print "%s songs retrieved from Google Music" % len(self.allSongs)

        self.db_entry_ids = (db.connect('entry-changed', self.entry_changed),
                             db.connect('entry-deleted', self.entry_deleted))

    def entry_deleted(self, entry, user_data):
        #Not deleted off disk, just removed from the player
        print user_data.get_string(RB.RhythmDBPropType.TITLE)


    def entry_changed(self, db, entry, changes):
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
            if change.prop is RB.RhythmDBPropType.HIDDEN:
                print "Song %s was deleted from disk" % entry.get_string(RB.RhythmDBPropType.TITLE)
                song = self.find_song(currentTitle, currentArtist, currentAlbum, currentGenre)
                #TODO: Delete song
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

            if song:
                self.api.change_song_metadata(song)

    def find_song(self, title, artist=None, album=None, genre=None):

        found = []

        for song in self.allSongs:
            if song['name'].lower() == title.lower():
                found.append(song)

        if len(found) > 1 and artist:
            for song in found:
                if not song['artist'].lower() == artist.lower():
                    found.remove(song)

        if len(found) > 1 and album:
            for song in found:
                if not song['album'].lower() == album.lower():
                    found.remove(song)

        if len(found) > 1 and genre:
            for song in found:
                if not song['genre'].lower() == genre.lower():
                    found.remove(song)

        if len(found) == 0:
            return None

        return found[0]


    def do_deactivate(self):
        if not self.api is None:
            self.api.logout()


