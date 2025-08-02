# Kodi Library Refresh

![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/LinogeFly/kodi-library-refresh/latest/total)

A service add-on for Kodi that helps to keep its libraries up to date.

The add-on watches for changes in media sources and automatically refreshes Kodi libraries, by performing library scans and clean ups, depending on how exactly files and directories were changed. For example, if new files were added, only library scan would be done, without running a clean up, which should run only if files get deleted or moved.

**Note:** Only local file system sources are currently supported. Network sources support is not yet implemented.

## Features

- Allows to refresh video library, music library, or both.
- Refreshes only when nothing is playing.

### Not yet implemented

- Network media sources.

## Installation

The add-on is not yet published to the official Kodi repository, so you have to install it from zip file for now. I haven't tried to publish the add-on simply because it's not yet finished. The add-on not in the shape I would feel comfortable publishing it. Things that needed to be done before publishing are:

1. More testing. The add-on hasn't been properly tested yet. I covered many use cases with automated tests, but not that many actual people have tried the add-on so far. I want to be sure it works as it should in different Kodi setups.
2. Network sources support. It is an important feature that I would like to get implemented before publishing to the official Kodi repository.

### Install from zip file

1. Download the latest installation file from [here](https://github.com/LinogeFly/kodi-library-refresh/releases/latest). Look for kodi-library-refresh-x.x.x.zip file under Assets.
2. Make sure you have "Unknown resources" setting enabled in Kodi. Find the setting under Settings > System > Add-ons > General section.
3. Go to Settings > Add-ons section, find "Install from zip file" action and then select the zip file you downloaded in step 1.

## Usage

There is almost no configuration for the add-on, and it's done intentionally that way. Just make sure the add-on is installed, enabled and it should work out of the box. The only thing you can configure is what libraries you want to get automatically refreshed. Use "Refresh videos" and "Refresh music" settings to configure that.

**Note:** If you add new media sources, after the add-on has been installed, you need to either restart Kodi or the add-on itself for the new media sources to be picked up by the add-on.

## Credits

Inspired by [Library Watchdog](https://kodi.tv/addons/nexus/service.librarywatchdog) add-on, which unfortunately is not supported anymore.
