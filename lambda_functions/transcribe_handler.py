import json
import urllib.parse
import boto3
import time
import requests
import logging
from botocore.exceptions import ClientError

print('Loading function')

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        job_name = key
        job_uri = "s3://skim-meeting/" + key
        
        transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='mp4',
        LanguageCode='en-US'
        )
        
        print("Reached here")

        while True:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            print(status['TranscriptionJob']['TranscriptionJobStatus'])
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            if job_status in ['COMPLETED', 'FAILED']:
                print(f"Job {job_name} is {job_status}.")
                if job_status == 'COMPLETED':
                    print(
                        f"Download the transcript from\n"
                        f"\t{status['TranscriptionJob']['Transcript']['TranscriptFileUri']}.")
                break
            print("Not ready yet...")
            time.sleep(5)
        print(status)
        
        url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        r = requests.get(url, allow_redirects=True)
        
        print(r.content)
    
        my_json = r.content.decode('utf8')
        print(my_json)
        
        data = json.loads(my_json)
        s = json.dumps(data, indent=4, sort_keys=True)
        
        finaldata = data["results"]["transcripts"][0]["transcript"]
        
        print(type(finaldata))
        print(finaldata)
    
        file = '/tmp/' + key + ".txt"
        
        text_file = open(file, "w")
        n = text_file.write(finaldata)
        text_file.close()
        
        lastIndex = key.rfind('.')
        key = key[0:lastIndex]

        
        try:
            response = s3.upload_file(file, "skim-meeting-text", key)
            print(response)
        except ClientError as e:
            logging.error(e)
            print(False)
        print(True)

        
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

