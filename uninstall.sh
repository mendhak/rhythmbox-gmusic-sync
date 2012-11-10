#Remove the files
rm -r ~/.local/share/rhythmbox/plugins/gmusicsync

#Remove the settings schema
sudo rm /usr/share/glib-2.0/schemas/org.gnome.rhythmbox.plugins.gmusicsync.gschema.xml
sudo glib-compile-schemas /usr/share/glib-2.0/schemas