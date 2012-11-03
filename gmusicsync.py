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
        for i in range(0,changes.n_values):
            change = changes.get_nth(i)
            if change.prop is RB.RhythmDBPropType.ALBUM:
                print "Album changed from %s to %s" % (change.old, change.new)
            if change.prop is RB.RhythmDBPropType.HIDDEN:
                print "Song %s was deleted from disk" % entry.get_string(RB.RhythmDBPropType.TITLE)
            if change.prop is RB.RhythmDBPropType.ARTIST:
                print "Artist was changed from %s to %s" % (change.old, change.new)
            if change.prop is RB.RhythmDBPropType.RATING:
                print "Assigned a rating of %s" % change.new
            if change.prop is RB.RhythmDBPropType.GENRE:
                print "New genre assigned is %s" % change.new
            if change.prop is RB.RhythmDBPropType.TITLE:
                print "Title changed from %s to %s" % (change.old, change.new)


    def do_deactivate(self):
        if not self.api is None:
            self.api.logout()


