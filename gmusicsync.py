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
        self.player_cb_ids = (
        sp.connect ('playing-song-changed', self.playing_entry_changed),
        )

    def playing_entry_changed (self, sp, entry):
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
