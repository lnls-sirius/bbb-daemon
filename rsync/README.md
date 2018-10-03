# Beaglebone Black Rsync Client

Using rsync package to synchronize files and libraries used by Controls Group in its Beaglebones.
The rsync daemon must run on a server ($RSYNC_SERVER), which must contain all files up to date.


For libraries, files are syncronized and library rebuilded automatically.


### Running rsync_beaglebone.sh
Rsync updates one project by now.
Call the script with project name as argument: `./rsync_beaglebone.sh project-name` 


### rsync_beaglebone.sh steps
- Check whether server is up
- Check if there are updates available for current project
- If so, update files and rebuild libraries (if needed)
