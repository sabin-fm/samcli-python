import json
import logging
import time
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class AWSWrapper():
    """Encapsulates Amazon Services"""
    
    def __init__(self):
        """
        :return: sns_resource: A Boto3 Amazon SNS resource.
        :return: dynamo_db: A Boto3 Amazon DynamoDB resource.
        """
        logger.info("Intializing AWS Services")
        try:
            self.sns_resource = boto3.resource('sns')
            self.dynamo_db = boto3.resource('dynamodb')
            self.boto3 = boto3
        except ClientError:
            logger.exception("Couldn't initialize AWS services")
            raise

    @staticmethod
    def get_dynamo_db_table(table_name: str):
        """Get the DynamoDB table
        Args:
            table_name (str): Name of the DynamoDB Table
        Returns:
            Dynamodb Table: Api to the DynamoDB Table
        """
        logger.info("Gettting DynamoDB table : %s" %table_name)
        try:
            return AWSWrapper().dynamo_db.Table(table_name)
        except ClientError:
            logger.exception("Couldn't initialize DynamoDB table: %s" %table_name)
            raise

    @staticmethod
    def get_cognito_client(cognito_name: str, region_name: str):
        """Get the Cognito service

        Args:
            cognito_name (str): Name of the cognito
            region_name (str): region name

        Returns:
            Cognito Service: service to use the cognito api
        """
        logger.info("Gettting Cognito : %s in Region: %s" %(cognito_name,region_name))
        try:
            return AWSWrapper().boto3.client(cognito_name, region_name)
        except ClientError:
            logger.exception("Couldn't initialize Cognito: %s in region : %s" %(cognito_name,region_name))
            raise