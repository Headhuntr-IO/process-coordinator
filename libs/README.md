# Libs
All the Python libraries in one layer so we dont need to re-upload the entire weight of the project whenever we introduce some code change

## Build Instructions
```
cd libs
pip3 install -t python -r requirements.txt
zip -r libs-latest.zip python/*
aws s3 cp libs-latest.zip s3://hhv2.headhuntr.io.deployment/python/libs-latest.zip
```