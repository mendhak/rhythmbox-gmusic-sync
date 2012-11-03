from gi.repository import GObject, Peas, RB
from gmusicsyncconfig import GMusicSyncConfigDialog

class GMusicSync(GObject.Object, Peas.Activatable):
    """
    This is an 'empty' Rhythmbox plugin which invokes another Python script to control Rhythmbox.
    """

    proc = None
    __gtype_name = 'GMusicSync'
    object = GObject.property(type=GObject.Object)

    def do_activate(self):
        sp = self.object.props.shell_player
        db = self.object.props.db

        self.player_cb_ids = (
                         sp.connect('playing-song-changed', self.playing_entry_changed),
                         sp.connect('playing-song-property-changed', self.playing_entry_property_changed  ))

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


    def playing_entry_property_changed(self, sp, uri, property, old, newvalue):
        if property != "playback-error":
            print sp
            print uri
            print property
            print old
            print newvalue


    def playing_entry_changed (self, sp, entry):
        if entry is not None:
            try:
                print entry.get_string(RB.RhythmDBPropType.TITLE)
            except:
                print "Error getting title"

            try:
                print entry.get_string(RB.RhythmDBPropType.ARTIST)
            except:
                print "Error getting artist"

            try:
                print entry.get_double(RB.RhythmDBPropType.RATING)
            except:
                print "Error getting rating"

            try:
                print entry.get_string(RB.RhythmDBPropType.ALBUM)
            except:
                print "Error getting album"


    def do_deactivate(self):
        pass


