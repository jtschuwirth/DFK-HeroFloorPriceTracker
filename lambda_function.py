import boto3
import os
from dotenv import load_dotenv
from functions.saveFloorPrices import saveAllFloorPrices


load_dotenv()

my_session = boto3.session.Session(
        aws_access_key_id=os.environ.get("ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("SECRET_KEY"),
        region_name = "us-east-1",
    )
table = my_session.resource('dynamodb').Table("dfk-herofloorprice")

def lambda_handler(event, context):
    return saveAllFloorPrices("dfk", table)