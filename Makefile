# Set up
# create access key for uploader SA
# yc iam access-key create --service-account-id ajeklq3j91e74ietc7ja
# put to ~/.aws/credentials under new profile
# [alice-difficult-worlds-uploader]
# aws_access_key_id = YCAJEOLpVRB42MiTnGVXAuSEb
# aws_secret_access_key = YCNJGA...

# Update code source in serverless function
# https://console.cloud.yandex.ru/folders/b1g98s4e5ps42bvqt9so/functions/functions/d4e741su5591436i201i/editor

.PHONY: upload

archive:
	mkdir -p target
	zip -r target/difficult-words.zip adapter domain resources *.py *.txt

upload: archive
	aws --profile alice-difficult-worlds-uploader --endpoint-url=https://storage.yandexcloud.net/ s3 cp target/difficult-words.zip s3://alice-difficult-words-code/prod/difficult-words.zip
