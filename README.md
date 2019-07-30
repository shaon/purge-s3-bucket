# purge-s3-bucket

```
usage: aws-purge-s3-buckets.py [-h] --profile PROFILE [--region REGION]
                               [--prefix PREFIX [PREFIX ...]] [--ignore]
                               [--exec] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  --profile PROFILE     name of the profile to use.
  --region REGION       region name.
  --prefix PREFIX [PREFIX ...]
                        finds buckets with prefix, can be a list e.g --prefix
                        one two three.
  --ignore              ignore the buckets with the prefix.
  --exec                enable bucket deletion. Without this flag deleted
                        buckets will only be displayed.
  --debug               Debug mode.

```
