from gi.repository import GObject, Peas, RB



class TrayIcon(GObject.Object, Peas.Activatable):
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
        print entry.get_string(RB.RhythmDBPropType.TITLE)

    def entry_changed(self, db, entry, changes):
        try:
            while True:
                change = changes.values
                print change.prop
                changes.remove(0)
        except:
            pass

#        try:
#            while True:
#                  change = changes.values
#
#                  if change.prop is RB.RhythmDBPropType.ALBUM:
#                      # called when the album of a entry is modified
#                      self._entry_album_modified(entry, change.old, change.new)
#
#                  elif change.prop is RB.RhythmDBPropType.HIDDEN:
#                      # called when an entry gets hidden (e.g.:the sound file is
#                      # removed.
#                      self._entry_hidden(db, entry, change.new)
#
#                  elif change.prop is RB.RhythmDBPropType.ARTIST:
#                      # called when the artist of an entry gets modified
#                      self._entry_artist_modified(entry, change.old, change.new)
#
#                  elif change.prop is RB.RhythmDBPropType.ALBUM_ARTIST:
#                      # called when the album artist of an entry gets modified
#                      self._entry_album_artist_modified(entry, change.new)
#
#                  # removes the last change from the GValueArray
#                  changes.remove(0)
#        except:
#        # we finished reading the GValueArray
#            pass

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
