#!/usr/bin/env python

import os
import shutil

# Copy files to ~/.local/share/plugins/rhythmbox/gmusicsync
# TODO: Implement this copying

# Copy schema file to /usr/share/glib-2.0/schemas/
shutil.copy('org.gnome.rhythmbox.plugins.gmusicsync.gschema.xml', '/usr/share/glib-2.0/schemas/org.gnome.rhythmbox.plugins.gmusicsync.gschema.xml')

# Run glib-compile-schemas /usr/share/glib-2.0/schemas
os.system('glib-compile-schemas /usr/share/glib-2.0/schemas')

#
#
#def run(self):
#        # Call parent
#        install_data.run(self)
#
#        # Execute commands after copying
#        os.system('glib-compile-schemas %s/share/glib-2.0/schemas' % self.install_dir)
#
#setup(name="gmusicsync",
#      cmdclass={"install_data": post_install},
#      version="0.11",
#      description="A Rhythmbox plugin to send metadata changes to Google Music",
#      author="Mendhak",
#      author_email="gmusicsync@mendhak.com",
#      url="http://github.com/mendhak/rhythmbox-gmusiscync",
#      data_files=[
#          ("share/rhythmbox/plugins/ampache", ["ampache-prefs.ui", "ampache.ico", "ampache.png"]),
#          ("share/glib-2.0/schemas", ["org.gnome.rhythmbox.plugins.gmusicsync.gschema.xml"]),
#          ],
#      )