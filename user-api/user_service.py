
import logging
import json
import os
from enum import Enum
from aws_wrapper import AWSWrapper

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TABLES(Enum):
    """Dynamo Tables used

    Args:
        Enum (Tables): Name of the tables with key and value

    Returns:
        Table: Dynamo DB table of given table name
    """
    USER_TABLE = "user"

    @staticmethod
    def get_table(table_name_enum: Enum):
        """Get the DynamoDB table

        Args:
            table_name_enum (Enum): Enum of the table with env as key and default as value

        Returns:
            Table: Dynamo DB table of given table name
        """
        aws_service = AWSWrapper()
        table_name = os.getenv(table_name_enum.name, table_name_enum.value)
        return aws_service.get_dynamo_db_table(table_name)


class COGNITO(Enum):
    """AWS Cognito

    Args:
        Enum (Cognito Variable): Variable for cognito
    """
    COGNITO_NAME = "cognito-idp"
    COGNITO_REGION = "us-east-1"
    COGNITO_USER_POOL_ID = "us-east-1_zHG6ezXPp"

    @staticmethod
    def get_cognito(cognito_name_enum: Enum, cognito_region_enum: Enum):
        """Get Cognito service client

        Args:
            cognito_name_enum (_type_): Enum with Cognito Name and Value 
            cognito_region_enum (_type_): Enum with Cognito Region and Value 

        Returns:
            Cognito Client: Cognito Client api 
        """
        aws_service = AWSWrapper()
        cognito_name = os.getenv(
            cognito_name_enum.name, cognito_name_enum.value)
        cognito_region = os.getenv(
            cognito_region_enum.name, cognito_region_enum.value)
        return aws_service.get_cognito_client(cognito_name, cognito_region)

    @staticmethod
    def get_user_pool_id(cognito_user_pool_id_enum: Enum) -> str:
        """Get Cognito Pool Id

        Args:
            cognito_user_pool_id_enum (_type_): Enum with Cognito User Pool Id and Value 

        Returns:
            String: Cognito User Pool Id
        """
        return os.getenv(cognito_user_pool_id_enum.name, cognito_user_pool_id_enum.value)


user_table = TABLES.get_table(TABLES.USER_TABLE)
cognito_service = COGNITO.get_cognito(
    COGNITO.COGNITO_NAME, COGNITO.COGNITO_REGION)
cognito_user_pool_id = COGNITO.get_user_pool_id(COGNITO.COGNITO_USER_POOL_ID)


class UserService():
    """ Services for user
    """

    def __init__(
        self,
        event,
        context
    ):
        logger.info("Event : %s" % event)
        logger.info("Context: %s" % context)
        self._event = event
        self._context = context
        self.query_string = event.get('queryStringParameters', None)
        try:
            requestBody = event.get('body', None)
            if requestBody:
                self.requestBody = json.loads(requestBody)
        except json.JSONDecodeError:
            logger.exception("Could not parse json on event: %s" % event)
            raise

    @staticmethod
    def save_user_to_cognito(email: str, isDionysusAdmin: bool):
        """Adde user to Cognito User Pool

        Args:
            email (str): User email
            isDionysusAdmin (bool): Status if user is admin or not

        Returns:
            Cognito User: User info created in the Cognito User Pool
        """
        try:
            response = cognito_service.admin_create_user(
                UserPoolId=cognito_user_pool_id,
                Username=email,
                UserAttributes=[{"Name": "email", "Value": email}, {"Name": "email_verified", "Value": "true"},
                                {"Name": "custom:isDionysusAdmin", "Value": str(isDionysusAdmin)}],
                DesiredDeliveryMediums=['EMAIL'])
            return response
        except Exception as error:
            logger.exception('Error while saving user to cognito ')
            return 500, {'Message': 'Error while saving user to cognito ', 'Error': error}


    @staticmethod
    def deleteUserFromCognito(username: str):
        """Remove User from Cognito User Pool

        Args:
            username (str): Email of the user to remove

        Returns:
            Cognito User: User info deleted in the Cognito User Pool
        """
        return cognito_service.admin_delete_user(UserPoolId=cognito_user_pool_id, Username=username)

    @staticmethod
    def remove_duplicates(l: list):
        """Remove duplicate in given list

        Args:
            l (list): List of string

        Returns:
            List: List of string removing duplicates
        """
        final = {}
        norm = []
        for item in l:
            if item not in final:
                final[item] = 1
                norm.append(item)
        return norm

    def getUser(self):
        """Get a single user info by email

        Args:
            email (str): email of the user

        Returns:
            User: user information
        """
        try:
            if self.query_string:
                user_email: str = self.query_string.get('email')
            else:
                logger.error("No email passed")
                raise Exception("No email passed")
            response = user_table.get_item(
                Key={
                    'email': user_email
                }
            )
            if 'Item' in response:
                return 200, response['Item']
            else:
                logger.error("User info of Email : % not found" % user_email)
                return 404, {"Message": 'Email %s not found' % user_email}
        except Exception as error:
            logger.exception('Error while getting user ')
            return 500, {'Message': 'Error while getting user ', 'Error': error}

    def getUsers(self):
        """Get all users info

        Returns:
            List[User]: list of user info
        """
        try:
            response = user_table.scan()
            result = response['Items']
            while 'LastEvaluateKey' in response:
                response = user_table.scan(
                    ExclusiveStartKey=response['LastEvaluateKey'])
            body = {
                'users': result
            }
            return 200, body

        except Exception as error:
            logger.exception('Error while getting all users')
            return 500, {'Message': 'Error while getting all users ', 'Error': error}

    def saveUser(self):
        """Save a user info

        Args:
            requestBody (User): User info

        Returns:
            User: User info
        """
        try:
            if self.requestBody:
                user_email: str = self.requestBody.get('email')
                dionysus_admin_status = self.requestBody.get('isDionysusAdmin')
            else:
                logger.error("No email or admin status passed")
                raise Exception("No email or admin status passed")
            self.save_user_to_cognito(user_email, dionysus_admin_status)
            response = user_table.put_item(Item=self.requestBody)
            body = {
                'operation': 'SAVE',
                'Message': 'Success',
                'User': response
            }
            return 200, body

        except Exception as error:
            logger.exception('Error while saving user')
            return 500, {'Message': 'Error while saving user', 'Error': error}

    def modifyUser(self):
        try:
            if self.requestBody:
                user_email: str = self.requestBody.get('email')
                updateKeys: list = self.requestBody.get('updateKeys')
                updateValues: list = self.requestBody.get('updateValues')
            else:
                logger.error("No email or updatekeys or update values passed")
                raise Exception(
                    "No email or updatekeys or update values passed")

            index = 0
            for updateKey in updateKeys:
                response = user_table.update_item(
                    Key={
                        'email': user_email
                    },
                    UpdateExpression='set %s = :value' % updateKey,
                    ExpressionAttributeValues={
                        ':value': updateValues[index]
                    },
                    ReturnValues='UPDATED_NEW'
                )
                index += 1
            body = {
                'operation': 'UPDATE',
                'Message': 'Success',
                'UpdateAttributes': response
            }
            return 200, body

        except Exception as error:
            logger.exception('Error while updating user')
            return 500, {'Message': str(error)}

    def deleteUser(self):
        try:
            if self.requestBody:
                user_email: str = self.requestBody.get('email')
            else:
                logger.error("No email passed")
                raise Exception("No email passed")

            self.deleteUserFromCognito(user_email)
            response = user_table.delete_item(
                Key={
                    'email': user_email
                },
                ReturnValues='ALL_OLD'
            )
            body = {
                'operation': 'DELETE',
                'Message': 'Success',
                'deletedUser': response
            }
            return 200, body

        except:
            logger.exception('Error while deleting user')
            return 500, {'Message': 'Error while deleting user'}

    def updateSignUpProgress(self):
        if self.requestBody:
            user_email: str = self.requestBody.get('email')
            pageIndex = self.requestBody.get('page_index')
            if "goals" in self.requestBody:
                goals = self.requestBody['goals']
            else:
                goals = []
        else:
            logger.error("No email or pageIndex passed")
            raise Exception("No email or pageIndex passed")

        onBoarding = False
        if pageIndex == "4":
            onBoarding = True
        try:
            response = user_table.update_item(
                Key={
                    'email': user_email
                },
                UpdateExpression='SET page_index= :val1,onBoarding= :val2, goals= :val3',
                ExpressionAttributeValues={
                    ':val1': pageIndex,
                    ':val2': onBoarding,
                    ':val3': goals
                },
                ReturnValues='UPDATED_NEW'
            )
            body = {
                'operation': 'UPDATE',
                'Message': 'Success',
                'UpdateAttributes': response
            }
            logger.exception(response)
            return 200, body

        except Exception as error:
            logger.exception('Error while updating user')
            return 500, {'Message': str(error)}

    def patchhormonalTracker(self):
        if self.requestBody:
            user_email: str = self.requestBody.get('email')
            updateValues: str = self.requestBody.get('updateValues')
        else:
            logger.error("No email or updateValues passed")
            raise Exception("No email or updateValues passed")
        self.query_string = {"email": user_email}
        status, user = self.getUser()
        update = list()
        if 'hormonal_tracker' in user:
            update = user.get('hormonal_tracker')
            update.append(updateValues)
        else:
            update.append(updateValues)
        self.requestBody = {
            "email": user_email,
            "updateKeys": ["hormonaltracker_flag", "hormonal_tracker"],
            "updateValues": [True, self.remove_duplicates(update)]
            }
        return self.modifyUser()

    def deletehormonalTracker(self):
        if self.query_string:
            user_email: str = self.query_string.get('email')
            updateValues: str = self.query_string.get('updateValues')
        else:
            logger.error("No email or updateValues passed")
            raise Exception("No email or updateValues passed")

        self.query_string = {"email": user_email}
        status, user = self.getUser()
        update = list()
        if 'hormonal_tracker' in user:
            update = user.get('hormonal_tracker')
            update.remove(updateValues)
        else:
            update.remove(updateValues)
        self.requestBody = {
            "email": user_email,
            "updateKeys": ["hormonaltracker_flag", "hormonal_tracker"],
            "updateValues": [True, self.remove_duplicates(update)]
            }
        return self.modifyUser()
    
    def patchJournal(self):
        if self.requestBody:
            user_email: str = self.requestBody.get('email')
            updateValues: str = self.requestBody.get('journal')
        else:
            logger.error("No email or updateValues passed")
            raise Exception("No email or updateValues passed")

        self.query_string = {"email": user_email}
        status, user = self.getUser()
        update = list()
        if 'journal_text' in user:
            update = user.get('journal_text')
            update.append(updateValues)
        else:
            update.append(updateValues)
        self.requestBody = {
            "email": user_email,
            "updateKeys": ["journal_text"],
            "updateValues": [self.remove_duplicates(update)]
            }
        return self.modifyUser()
