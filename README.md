# purge-s3-bucket

```
usage: aws-purge-s3-buckets.py [-h] --profile PROFILE [--region REGION]
                               [--prefix PREFIX [PREFIX ...]] [--ignore]
                               [--dry-run]

optional arguments:
  -h, --help            show this help message and exit
  --profile PROFILE     name of the profile to use.
  --region REGION       region name.
  --prefix PREFIX [PREFIX ...]
                        finds buckets with prefix, can be a list
                        e.g --prefix one two three.
  --ignore              ignore the buckets with the prefix.
  --dry-run             shows the buckets that will be deleted when run
                        without this.
```
