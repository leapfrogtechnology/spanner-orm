# Google Cloud Spanner ORM

```
product:
  name: Google Cloud Spanner ORM
  short_name: spannerorm
  url: https://cloud.google.com/spanner/docs
  description:
    spannerdb ORM is a highly scalable, efficient Google Cloud Spanner ORM.
```

## Installation
- Install pip
```
sudo apt-get install python-pip
```
- Install client library
```
pip install --upgrade google-cloud-spanner
```
- Go to the `GCP Console` > `Service accounts`
- Download key from service account list by clicking at `action`  > `create key`
- export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"