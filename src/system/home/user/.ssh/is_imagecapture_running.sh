#!/bin/bash

if [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/imagecapture.py" | /usr/bin/wc -l` < 1 ]]; then
  logger -i -t imagecapture "Imagecapture is not running, starting imagecapture."
  /usr/bin/python /usr/local/bin/imagecapture.py -C;
  /usr/bin/python /usr/local/bin/imagecapture.py -L -A -c -e 'sshmonitorapp@gmail.com' -p 'hkeyscwhgxjzafvj' &
elif [[ `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/imagecapture.py" | /usr/bin/wc -l` > 1 ]]; then
  logger -i -t imagecapture "Restarting imagecapture."
  /usr/bin/sudo /bin/kill -9 `/bin/ps aux | /bin/egrep -i "[0-9]{1,2}:[0-9]{1,2} /usr/bin/python /usr/local/bin/imagecapture.py" | /usr/bin/awk '{print $2}'`;
  /usr/bin/python /usr/local/bin/imagecapture.py -C;
  /usr/bin/python /usr/local/bin/imagecapture.py -L -A -c -e 'sshmonitorapp@gmail.com' -p 'hkeyscwhgxjzafvj' &
else
  logger -i -t imagecapture "Imagecapture is running.";
fi
