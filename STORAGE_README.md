'''
Use this if you want to use Google Cloud Storage
''' 

# STORAGES = {
#     "default": {
#         "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
#         "OPTIONS": {
#             "bucket_name": config('AWS_STORAGE_BUCKET_NAME'),
#             "location": "",
#             "default_acl": None, 
#         },
#     },
#     "staticfiles": {
#         "BACKEND": "django.core.files.storage.FileSystemStorage",
#         "OPTIONS": {
#             "location": os.path.join(BASE_DIR, "staticfiles"),
#             "base_url": STATIC_URL,
#         },
#     },
# }

# GS_CREDENTIALS_FILE = os.path.join(BASE_DIR, config('GOOGLE_APPLICATION_CREDENTIALS'))
# GS_CREDENTIALS = service_account.Credentials.from_service_account_file(GS_CREDENTIALS_FILE)

# 🔥 Make sure GCS SDK can also see the credentials
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GS_CREDENTIALS_FILE

# GS_BUCKET_NAME = config('GCS_BUCKET_NAME')
# GS_DEFAULT_ACL = 'publicRead'
# GS_QUERYSTRING_AUTH=False


# Set media URL (e.g., for serving images from GCS)
# MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/'
