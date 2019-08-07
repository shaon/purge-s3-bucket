import logging
import boto3
import argparse
import time
import multiprocessing

parser = argparse.ArgumentParser()
parser.add_argument("--profile", help="name of the profile to use.", required=True)
parser.add_argument("--region", help="region name.")
parser.add_argument("--prefix", nargs='+', help="finds buckets with prefix, can be a list e.g --prefix one two three.")
parser.add_argument("--ignore", action="store_true", help="ignore the buckets with the prefix.")
parser.add_argument("--exec",
                    default=False,
                    action="store_true",
                    help="enable bucket deletion. Without this flag deleted buckets will only be displayed.")
parser.add_argument("--debug", action="store_true", help="Debug mode.")
args = parser.parse_args()

RETRY = 6
RETRY_WAIT = 10

if not args.profile:
    logging.error("Profile not found!")
    exit(1)

session = boto3.Session(profile_name=args.profile)
s3 = session.resource('s3')
s3client = session.client('s3')

if not args.exec:
    print("Dry run. No buckets deleted, only displayed. Pass --exec flag for deletion.")
else:
    print("--exec flag found. Deleting buckets.")
    time.sleep(2)  # give time to ctrl+z if needed.


def prefix_matched(bucket_name):
    for p in args.prefix:
        if bucket_name.startswith(p):
            return True
    return False


def found_in_region(bucket_name):
    try:
        region_name = s3client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
    except s3client.exceptions.NoSuchBucket as e:
        return False

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

    if valid_in_region and valid_for_prefix:
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
    if args.exec:
        for i in range(RETRY):
            empty_bucket(bucket)
            response = s3client.list_objects_v2(Bucket=bucket.name)
            if 'Contents' in response:
                logging.info("Retrying in %d seconds" % RETRY_WAIT)
                time.sleep(RETRY_WAIT)
                continue
            break

        for i in range(RETRY):
            empty_bucket(bucket)
            response = s3client.list_object_versions(Bucket=bucket.name)
            if 'Versions' in response:
                logging.info("Retrying in %d seconds" % RETRY_WAIT)
                time.sleep(RETRY_WAIT)
                continue
            break

        try:
            bucket.delete()
        except:
            raise Exception("Failed to delete bucket.")

    print("Deleted: " + bucket.name)


def main():
    logging.info("Getting the valid buckets to be purged...")
    buckets = s3client.list_buckets()

    if 'Buckets' not in buckets:
        raise Exception("S3 doesn't have any buckets.")
    start = time.time()
    jobs = []
    for bucket in buckets['Buckets']:
        bucket_name = bucket['Name']
        if is_valid(bucket_name):
            s3_Bucket = s3.Bucket(bucket_name)
            p = multiprocessing.Process(target=delete_bucket, args=(s3_Bucket,))
            p.start()
            jobs.append(p)
    for job in jobs:
        job.join()

    end = time.time()
    print(f"Time elapsed: {end - start} seconds.")


if __name__ == "__main__":
    main()
