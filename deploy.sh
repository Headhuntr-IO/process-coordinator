#eval "export AWS_REGION=\$$1_AWS_REGION"
#eval "export COMMONS_LAYER_NAME=\$$1_COMMONS_LAYER_NAME"
#eval "export DELEGATE_FUNCTION_NAME=\$$1_DELEGATE_FUNCTION_NAME"

#ls build
#aws s3 sync s3://$AWS_S3_BUCKET/lambda/ s3://$AWS_S3_BUCKET.$AWS_REGION/lambda/
#new_layer_arn="$(aws lambda publish-layer-version --layer-name $COMMONS_LAYER_NAME --region $AWS_REGION --description "commons build:$BITBUCKET_BUILD_NUMBER" --content S3Bucket=$AWS_S3_BUCKET.$AWS_REGION,S3Key=lambda/commons/commons-$BITBUCKET_BUILD_NUMBER.zip --compatible-runtimes python3.8 --output json | jq -r .LayerVersionArn)"
#aws lambda update-function-code --function-name $DELEGATE_FUNCTION_NAME --s3-bucket $AWS_S3_BUCKET.$AWS_REGION --region $AWS_REGION --s3-key lambda/delegate/delegate-$BITBUCKET_BUILD_NUMBER.zip
#aws lambda update-function-configuration --function-name $DELEGATE_FUNCTION_NAME --description "delegate build:$BITBUCKET_BUILD_NUMBER" --layers $new_layer_arn --region $AWS_REGION


aws lambda update-function-code --function-name main --s3-bucket hhv2.headhuntr.io.deployment --region us-east-1 --s3-key python/main-latest.zip