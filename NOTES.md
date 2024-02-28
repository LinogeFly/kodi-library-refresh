# Notes

## To-do

- IMPROVE: Automated release creation on GitHub.
- IMPROVE: Run tests automatically for Windows and Linux on GitHub.
- IMPROVE: Remove `xbmc.Monitor` base class from `Settings` class.
- IMPROVE: Cache supported media that we get every time by calling `xbmc.getSupportedMedia`. The fetching and caching can be added to Library class and then passed to Watcher as a dependency, as it already calls getMediaSources.

### To-do completed

- BEFORE RELEASE: README.md
- BEFORE RELEASE: tests/README.md
- BEFORE RELEASE: Name
- BEFORE RELEASE: Logo
- INVESTIGATE: Check if it's possible to get notified if a new media source gets added (nope).
- BEFORE RELEASE: Add MIT license
- BEFORE RELEASE: Use double quotes for logging messages.
- BEFORE RELEASE: Make sure log.debug actually logs with "debug" level. Review all the places and maybe change some parts to log with "info" level.
- BEFORE RELEASE: Remove `sandbox` directory.
- FEATURE: Don't start the updating tasks if something is playing.
- FEATURE: Task execution debounce.
- BUG: Exception in watcher.py/EventHandler hangs Kodi upon exit.
  - [x] Fix
  - [x] Tests
- FEATURE: Watcher ignore rules.
  - [x] Skip hidden files.
  - [x] Skip not supported media files (xbmc.getSupportedMedia).
  - [x] Add more description for interesting places in code.
- BUG: Exceptions in Monitor subclasses should show error notifications.
- BUG: Exception in `Library.getMediaSources` makes add-on to hang.
- Tests. Tests. Tests.
- Get media sources from Kodi.
- BUG: If watchers can't be created the add-on can't stop properly and Kodi gets stuck when exiting.
- Add-on setting changes should re-create media source watches.
- Clean command manager queue if add-on settings change.
- Test what happens when an exception occurs in the task manager run function.
- Log a warning if there are more than one event handler at a time for clean/update commands in Monitor.
- OPTIONAL: Rename "task execute" concept to "task handle".

## Add-on name

Name ideas:

- Library Up-To-Dater
- Library Up-to-dater
- Library Auto Sync
- Library Auto Refresh
- Library Refresh
- Library Sync
- LibSync

Key words:

- Sync
- Up-to-date
- Update
- Refresh

Examples:

- <https://kodi.tv/addons/nexus/category/services>

## Add-on logo

Free SVG icons:

- <https://www.svgrepo.com/collection/industrial-sharp-ui-icons>
- <https://icon-icons.com/id/download/208637/SVG/512/>

## Automatic release creation

Examples:

- <https://github.com/XBMC-Addons/service.xbmc.versioncheck>

## Add-on examples

- <https://github.com/robweber/xbmclibraryautoupdate>
- <https://github.com/robweber/xbmcbackup>
- <https://github.com/CastagnaIT/plugin.video.netflix>
- <https://github.com/Heckie75/kodi-addon-timers> (has unit tests)
- <https://github.com/add-ons/plugin.video.redbull.tv> (has unit tests)
- <https://github.com/xbmc/metadata.themoviedb.org.python> (has unit tests)
- <https://github.com/HenrikDK/youtube-xbmc-plugin> (has unit tests)

## Architecture notes

Modules (or classes) design:

- Main. Does the following:
  - Starts and stops the watcher.
  - Restarts the watcher when settings change.
  - Hosts the commands queue.
  - Executes commands from the queue.
- Watcher. Does the following:
  - Creates watches for supplied paths
  - Starts
  - Stops
  - Adds commands into the queue to re-scan and clean the library.
- PathProvider. Does the following:
  - Returns all paths from Kodi media sources to be watched.
- SettingsManager. Does the following:
  - Returns setting values via methods
  - Raises an event when settings change (???)

## Debugging

### Watch logs

Linux:

```
tail -F -n 1000 ~/.kodi/temp/kodi.log | grep service.library-refresh --color=never
```

## Testing

### Create multiple files

Linux:

```
touch {001..010}.mkv
```

Windows (PowerShell):

```
new-item $(01..20 | %{"$_.mkv"})
```

### Create movie files - Set 1

Linux:

```
touch Conan.the.Barbarian.1982.mkv; \
touch Conan.the.Destroyer.1984.mkv; \
touch The.Terminator.1984.mkv; \
touch Commando.1985.mkv; \
touch Predator.1987.mkv; \
touch The.Running.Man.1987.mkv; \
touch Twins.1988.mkv; \
touch Total.Recall.1990.mkv; \
touch Kindergarten.Cop.1990.mkv; \
touch Terminator.2.Judgment.Day.1991.mkv; \
touch Last.Action.Hero.1993.mkv; \
touch True.Lies.1994.mkv; \
touch Eraser.1996.mkv; \
touch Jingle.All.the.Way.1996.mkv; \
touch The.Expendables.2010.mkv; \
touch The.Expendables.2.2012.mkv; \
touch The.Expendables.3.2014.mkv
```

Windows (PowerShell):

```
new-item "Conan.the.Barbarian.1982.mkv" -Force; `
new-item "Conan.the.Destroyer.1984.mkv" -Force; `
new-item "The.Terminator.1984.mkv" -Force; `
new-item "Commando.1985.mkv" -Force; `
new-item "Predator.1987.mkv" -Force; `
new-item "The.Running.Man.1987.mkv" -Force; `
new-item "Twins.1988.mkv" -Force; `
new-item "Total.Recall.1990.mkv" -Force; `
new-item "Kindergarten.Cop.1990.mkv" -Force; `
new-item "Terminator.2.Judgment.Day.1991.mkv" -Force; `
new-item "Last.Action.Hero.1993.mkv" -Force; `
new-item "True.Lies.1994.mkv" -Force; `
new-item "Eraser.1996.mkv" -Force; `
new-item "Jingle.All.the.Way.1996.mkv" -Force; `
new-item "The.Expendables.2010.mkv" -Force; `
new-item "The.Expendables.2.2012.mkv" -Force; `
new-item "The.Expendables.3.2014.mkv" -Force;
```

### Create movie files - Set 2

Linux:

```
touch Rocky.1976.mkv; \
touch Rocky.II.1979.mkv; \
touch Rocky.III.1982.mkv; \
touch First.Blood.1982.mkv; \
touch Rambo.First.Blood.Part.II.1985.mkv; \
touch Rocky.IV.1985.mkv; \
touch Cobra.1986.mkv; \
touch Over.the.Top.1987.mkv; \
touch Rambo.III.1988.mkv; \
touch 'Tango.&.Cash.1989.mkv'; \
touch Cliffhanger.1983.mkv; \
touch Demolition.Man.1983.mkv; \
touch Judge.Dredd.1995.mkv; \
touch Rambo.2008.mkv; \
touch The.Expendables.2010.mkv; \
touch The.Expendables.2.2012.mkv; \
touch The.Expendables.3.2014.mkv
```

Windows (PowerShell):

```
new-item "Rocky.1976.mkv" -Force; `
new-item "Rocky.II.1979.mkv" -Force; `
new-item "Rocky.III.1982.mkv" -Force; `
new-item "First.Blood.1982.mkv" -Force; `
new-item "Rambo.First.Blood.Part.II.1985.mkv" -Force; `
new-item "Rocky.IV.1985.mkv" -Force; `
new-item "Cobra.1986.mkv" -Force; `
new-item "Over.the.Top.1987.mkv" -Force; `
new-item "Rambo.III.1988.mkv" -Force; `
new-item "Tango.&.Cash.1989.mkv" -Force; `
new-item "Cliffhanger.1983.mkv" -Force; `
new-item "Demolition.Man.1983.mkv" -Force; `
new-item "Judge.Dredd.1995.mkv" -Force; `
new-item "Rambo.2008.mkv" -Force; `
new-item "The.Expendables.2010.mkv" -Force; `
new-item "The.Expendables.2.2012.mkv" -Force; `
new-item "The.Expendables.3.2014.mkv" -Force;
```

## Copy to HTPC

Mount remote file system:

```
sshfs root@192.168.1.102:/storage ~/htpc/ssh
```

Copy:

```
rsync -av --exclude=".*" --exclude="tests" --exclude="assets" --exclude="__pycache__" --delete . ~/htpc/ssh/.kodi/addons/service.library-refresh
```

Unmount:

```
fusermount -u ~/htpc/ssh
```
