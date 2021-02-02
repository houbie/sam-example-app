#! /bin/bash

DYNAMO_DIR=".dynamodb"
DYNAMO_JAR=$DYNAMO_DIR/DynamoDBLocal.jar
if [ ! -f "$DYNAMO_JAR" ]; then
  mkdir -p $DYNAMO_DIR
  cd "$DYNAMO_DIR"
  curl -O "https://s3-us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz"
  tar -xvzf dynamodb_local_latest.tar.gz
  rm dynamodb_local_latest.tar.gz
  cd ..
fi
