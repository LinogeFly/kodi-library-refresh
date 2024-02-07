#!/usr/bin/env bash

set -e          # script stops on error
set -u          # error if undefined variable
set -o pipefail # script fails if piped command fails

__addonName="service.library-refresh"

function get_package_version() {
    local regEx="^v([0-9]+\.[0-9]+\.[0-9]+).*$"
    local versionLine=$(head -n 1 changelog.txt)

    if [[ $versionLine =~ $regEx ]]
    then
        echo "${BASH_REMATCH[1]}"
    else
        echo "Unable to read the latest package version number from changelog.txt file." >&2
        exit 1
    fi
}

packageName="kodi-library-refresh-$(get_package_version)"

# Create, or re-create if exists, "dist" directory
[ -d dist ] && rm -r dist
mkdir dist

# Copy add-on files
rsync -av --exclude=".*" --exclude="*.sh" --exclude="*.md" --exclude="tests" --exclude="assets" --exclude="dist" --exclude="__pycache__" --delete . "dist/$__addonName"

# Create the release package
(cd dist && zip -r $packageName.zip $__addonName)

# Clean up
rm -r "dist/$__addonName"
