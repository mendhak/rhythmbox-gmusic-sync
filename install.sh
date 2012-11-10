
# Copy files to ~/.local/share/plugins/rhythmbox/gmusicsync
mkdir -p ~/.local/share/rhythmbox/plugins/gmusicsync/
cp -rf * ~/.local/share/rhythmbox/plugins/gmusicsync/

#Install pip and gmusicapi
sudo apt-get install python-pip
sudo pip install gmusicapi

# Copy schema file to /usr/share/glib-2.0/schemas/
sudo cp org.gnome.rhythmbox.plugins.gmusicsync.gschema.xml /usr/share/glib-2.0/schemas/org.gnome.rhythmbox.plugins.gmusicsync.gschema.xml

# Run glib-compile-schemas /usr/share/glib-2.0/schemas
sudo glib-compile-schemas /usr/share/glib-2.0/schemas

