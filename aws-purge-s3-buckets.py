import boto3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--profile", help="name of the profile to use.", required=True)
parser.add_argument("--region", help="region name.")
parser.add_argument("--prefix", nargs='+', help="finds buckets with prefix, can be a list e.g --prefix one two three.")
parser.add_argument("--ignore", action="store_true", help="ignore the buckets with the prefix.")
parser.add_argument("--dry-run", action="store_true", help="shows the buckets that will be deleted when run without this.")
args = parser.parse_args()

if not args.profile:
    print("Profile not found!")
    exit(1)

session = boto3.Session(profile_name=args.profile)
s3 = session.resource('s3')

def prefix_matched(bucket_name):
  for p in args.prefix:
    if bucket_name.startswith(p):
      return True
  return False

def found_in_region(bucket_name):
  region_name = s3.meta.client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']

  if region_name is None:
    region_name = "us-east-1"

  if region_name == args.region:
    return True
  return False

def is_valid(bucket_name):
  valid_in_region = True
  valid_for_prefix = True

  if args.region:
    valid_in_region = found_in_region(bucket_name)

  if args.prefix:
    if args.ignore:
      valid_for_prefix = not prefix_matched(bucket_name)
    else:
      valid_for_prefix = prefix_matched(bucket_name)

  if (valid_in_region and valid_for_prefix):
    return True
  return False

def empty_bucket(bucket):
  v = bucket.Versioning()
  if v.status == "Enabled":
    v.suspend()

  bucket.objects.all().delete()

  if v.status == "Suspended":
    bucket.object_versions.all().delete()

def delete_bucket(bucket):
  if not args.dry_run:
    empty_bucket(bucket)
    bucket.delete()

  print("Deleted: " + bucket.name)

def main():
  for bucket in s3.buckets.all():
    if is_valid(bucket.name):
      delete_bucket(bucket)

if __name__ == "__main__":
    main()
