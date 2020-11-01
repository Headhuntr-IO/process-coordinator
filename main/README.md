# Main
Home of our lambda codes

## Build Instructions
```
zip -g main-latest.zip *.py
aws s3 cp main-latest.zip s3://hhv2.headhuntr.io.deployment/python/main-latest.zip
```