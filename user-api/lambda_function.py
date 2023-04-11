import http
import boto3
import logging
from enum import Enum
from user_service import UserService

import json
from custom_encoder import CustomEncoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"

class HttpPath(Enum):
    HEALTH_PATH = "/health"
    USER_PATH = "/user"
    USERS_PATH = "/users"
    PROGRESS_PATH = "/user/signup_progress"
    HORMONAL_TRACKER_PATH = "/hormonalTracker"
    JOURNAL_PATH = "/journal"


def lambda_handler(event, context):

    httpMethod = event['httpMethod']
    path = event['path']
    user_service = UserService(event, context)


    if HttpMethod.GET.value.__eq__(httpMethod) and HttpPath.HEALTH_PATH.value.__eq__(path):
        status, response =  200, "All good"
    elif HttpMethod.GET.value.__eq__(httpMethod) and HttpPath.USER_PATH.value.__eq__(path):
        status, response =  user_service.getUser()
    elif HttpMethod.GET.value.__eq__(httpMethod) and HttpPath.USERS_PATH.value.__eq__(path):
        status, response =  user_service.getUsers()
    elif HttpMethod.POST.value.__eq__(httpMethod) and HttpPath.USER_PATH.value.__eq__(path):
        status, response =  user_service.saveUser()
    elif HttpMethod.PATCH.value.__eq__(httpMethod) and HttpPath.USER_PATH.value.__eq__(path):
        status, response =  user_service.modifyUser()
    elif HttpMethod.DELETE.value.__eq__(httpMethod) and HttpPath.USER_PATH.value.__eq__(path):
        status, response =  user_service.deleteUser()
    elif HttpMethod.PATCH.value.__eq__(httpMethod) and HttpPath.PROGRESS_PATH.value.__eq__(path):
        status, response =  user_service.updateSignUpProgress()
    elif HttpMethod.PATCH.value.__eq__(httpMethod) and HttpPath.HORMONAL_TRACKER_PATH.value.__eq__(path):
        status, response =  user_service.patchhormonalTracker()
    elif HttpMethod.DELETE.value.__eq__(httpMethod) and HttpPath.HORMONAL_TRACKER_PATH.value.__eq__(path):
        status, response =  user_service.deletehormonalTracker()
    elif HttpMethod.POST.value.__eq__(httpMethod) and HttpPath.JOURNAL_PATH.value.__eq__(path):
        status, response =  user_service.patchJournal()
    else:
        status, response = 404, 'Path Not Found'

    return buildResponse(status, response)

def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response
