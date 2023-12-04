#!/bin/bash

counter=1

for file in $(ls -1 | sort); do
    current_directory=$(pwd)
    series_name=$(basename "$(dirname "$(dirname "$current_directory")")")
    season_number=$(basename "$(dirname "$current_directory")")
    episode_number=$(printf "%02d" $counter)
    extension="${file##*.}"

    new_name="${series_name}_${season_number}_E${episode_number}.${extension}"

    # mv "$file" "$new_name"
    echo "$file -> $new_name"
    ((counter++))
done
