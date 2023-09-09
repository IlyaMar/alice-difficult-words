.PHONY: upload

archive:
	mkdir -p target
	zip -r target/difficult-words.zip adapter domain resources *.py *.txt

upload: archive
	aws --endpoint-url=https://storage.yandexcloud.net/ s3 cp target/difficult-words.zip s3://alice-difficult-words-code/prod/difficult-words.zip
