import random
from datetime import datetime

now = datetime.now()
num = random.randint(1,101)
with open('/tmp/rand.txt', 'a') as f:
    f.write('{} - Your random number is {}\n'.format(now, num))

# Guide to use Cron
# https://www.youtube.com/watch?v=EgrpfvBc7ks

# runs every minute every day
# * * * * * date > /tmp/test.txt
# * * * * * /(absolute path in Linux WSL)/python /(absolute path)/cron_script_to_run.py


# runs every hour every day (doing this for testing)
# 0 * * * * date > /tmp/test.txt
# 0 * * * * /(absolute path in Linux WSL)/python /(absolute path)/cron_script_to_run.py


# runs at 1:00 AM every day (will do after testing)
# 0 1 * * * date > /tmp/test.txt
# 0 1 * * * /(absolute path in Linux WSL)/python /(absolute path)/cron_script_to_run.py


# to edit cron (in terminal)
# crontab -e

# to view /tmp/test.txt output:
# cat /tmp/rand/txt