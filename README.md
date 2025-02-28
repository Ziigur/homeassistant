## activity_to_homeassistant.py

This is a python script which informs homeassistant that I am currently doing something with my computer.
The idea is that this script works with the motion sensor in the same room so that the lights will stay on even if the motion sensor does not detect any movement.

The service can be installed as a `systemctl` service to be run on the background.

### Known issues

- If using the script with laptop, lights go on even if I am on a different room with the laptop. Possible solution would be to detect if the computer is attached to an external monitor.
