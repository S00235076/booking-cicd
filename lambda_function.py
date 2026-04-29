import boto3
import json
import time
import os

client = boto3.client('stepfunctions')

STATE_MACHINE_ARN = os.environ['STATE_MACHINE_ARN']

# In-memory cache
cache = {}
CACHE_TTL = 120  # seconds

def lambda_handler(event, context):
    print("EVENT:", event)

    try:
        #  SUPPORT BOTH GET + POST

        if event.get("queryStringParameters"):
            body = event["queryStringParameters"]

        elif event.get("body"):
            body = json.loads(event["body"])

        else:
            body = event

        print("Parsed body:", body)

        # CACHE KEY
        key = json.dumps(body)
        current_time = time.time()

        # CACHE CHECK
        if key in cache:
            cached_response, timestamp = cache[key]

            if current_time - timestamp < CACHE_TTL:
                print("API CACHE HIT")
                return cached_response

        print("API CACHE MISS")

        # START STEP FUNCTION
        response = client.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps(body)
        )

        result = {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Booking started',
                'executionArn': response['executionArn']
            })
        }

        # STORE IN CACHE
        cache[key] = (result, current_time)

        return result

    except Exception as e:
        print("ERROR:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
