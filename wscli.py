#!/usr/bin/env python

import logging
import json

import boto3
import click
from pythonjsonlogger import jsonlogger

#intialize logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
LOGHANDLER = logging.StreamHandler()
FORMMATTER = jsonlogger.JsonFormatter()
LOGHANDLER.setFormatter(FORMMATTER)
log.addHandler(LOGHANDLER)

### Lambda Boto API Calls
def lambda_connection(region_name="us-east-1"):
    """Create Lambda Connection"""

    lambda_conn = boto3.client("lambda", region_name=region_name)
    extra_msg = {"region_name": region_name, "aws_service": "lambda"}
    log.info("instantiate lambda client", extra=extra_msg)    
    return lambda_conn

def parse_lambda_result(response):
    """Gets the results from a boto json response"""
    
    body = response['Payload']
    json_result = body.read()
    lambda_return_value = json.loads(json_result)
    return lambda_return_value

def invoke_lambda(func_name, lambda_conn, payload=None, 
                    invocation_type="RequestResponse"):
    """Calls a lambda function"""


    extra_msg = {"function_name": func_name, "aws_service": "lambda",
            "payload":payload}
    log.info("Calling lambda function", extra=extra_msg)
    if not payload:
        payload = json.dumps({"payload":"None"})
    
    response = lambda_conn.invoke(FunctionName=func_name,
                    InvocationType=invocation_type,
                    Payload=payload
    )
    log.info(response, extra=extra_msg)
    lambda_return_value = parse_lambda_result(response)
    return lambda_return_value

@click.group()
@click.version_option("1.0")
def cli():
    """Commandline Utility to Assist in Web Scraping"""

@cli.command("lambda")
@click.option("--func", default="scrape-yahoo-dev-return_player_urls", 
        help="name of execution")
@click.option("--payload", default='{"cli":"invoke"}', 
        help="name of payload")
def call_lambda(func, payload):
    """invokes lambda function
    
    ./wscli.py lambda
    """ 
    click.echo(click.style("Lambda Function invoked from cli:", bg='blue', fg='white'))
    conn = lambda_connection()
    lambda_return_value = invoke_lambda(func_name=func,
        lambda_conn=conn,
        payload=payload)
    formatted_json = json.dumps(lambda_return_value, sort_keys=True, indent=4)
    click.echo(click.style("Lambda Return Value Below:", bg='blue', fg='white'))
    click.echo(click.style(formatted_json,fg="red"))

if __name__ == "__main__":
    cli()