# Main
Home of our lambda codes

## Build Instructions
```
zip -g main-latest.zip *.py
aws s3 cp main-latest.zip s3://hhv2.headhuntr.io.deployment/python/main-latest.zip


aws lambda update-function-code --function-name main --s3-bucket hhv2.headhuntr.io.deployment --region us-east-1 --s3-key python/main-latest.zip
```