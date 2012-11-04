import rb
from gi.repository import GObject, Gtk, Gio, PeasGtk

class GMusicSyncConfigDialog(GObject.Object, PeasGtk.Configurable):
        __gtype_name__ = 'GMusicSyncConfigDialog'
        object = GObject.property(type=GObject.Object)

        def do_create_configure_widget(self):

                self.settings = Gio.Settings('org.gnome.rhythmbox.plugins.gmusicsync')
                self.ui = Gtk.Builder()
                self.ui.add_from_file(rb.find_plugin_file(self, 'gmusicsync-prefs.ui'))
                self.config_dialog = self.ui.get_object('config')


                self.username = self.ui.get_object("username_entry")
                self.username.set_text(self.settings['username'])

                self.password = self.ui.get_object("password_entry")
                self.password.set_visibility(False)
                self.password.set_text(self.settings['password'])

                self.allowdelete = self.ui.get_object("delete_entry")
                self.allowdelete.set_active(self.settings['deleteongmusic'])

                self.username.connect('changed', self.username_changed_cb)
                self.password.connect('changed', self.password_changed_cb)
                self.allowdelete.connect('toggled', self.allowdelete_changed)

                return self.config_dialog

        def allowdelete_changed(self, widget):
            self.settings['deleteongmusic'] = self.allowdelete.get_active()

        def username_changed_cb(self, widget):
                self.settings['username'] = self.username.get_text()

        def password_changed_cb(self, widget):
                self.settings['password'] = self.password.get_text()