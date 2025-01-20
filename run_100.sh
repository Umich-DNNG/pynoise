#!/bin/bash

# Path to the settings file
SETTINGS_FILE="settings/ra_MUSIC_config2_sim_100.json"

# Base directory for the input file
BASE_DIR="/Users/fdarby/University of Michigan Dropbox/ENGIN-Well-counter/DAF/MUSIC/MCNP/MCNPX-Polimi/config2/config2_100_nodes"

# Iterate from 0 to 99
for i in $(seq 0 99); do
  # Construct the new input file name
  INPUT_FILE="config2_dets_on_ifplate${i}_times.txt"

  # Update the settings file with the new input file
  jq --arg inputFile "$BASE_DIR/$INPUT_FILE" \
     '.["Input/Output Settings"]["Input file/folder"] = $inputFile' \
     "$SETTINGS_FILE" > tmp_settings.json && mv tmp_settings.json "$SETTINGS_FILE"

  # Run the Python command
  python main.py -c i a ra_MUSIC_config2_sim_100 r m x x q

done

echo "Simulation runs completed for all iterations."

