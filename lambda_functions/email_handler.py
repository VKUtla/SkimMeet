import sys
import urllib
import boto3
import pymysql
def lambda_handler(event, context):
    rds_host = 'skim.cbzr5ukrzql9.us-east-1.rds.amazonaws.com'
    name = 'admin'
    password = 'skim1234'
    db_name = 'skim'
    try:
        print("Loading function ...")
        sns = boto3.client("sns", region_name="us-east-1", aws_access_key_id="ASIARXYWXFBEUUUBJM7L",
                           aws_secret_access_key="B0OgJDQSNmv2tjctmPSKrs2VMxg5pOLeyalQC88+",
                           aws_session_token="FwoGZXIvYXdzELX//////////wEaDM0oW8Mv4vpIcVDWXyK/AfHAAQYtloxdERtbXLeVKOlOgmuQdERlZv8afBAn27vcP0whgVHB5o8d/PXM7CsRE7t3DXv1OUYBOuk52OW+mR1aHtgBt3yo7PrIWRDZ+MOb0y5vaqC/zkKoKzGW+a5TFBQb6sADEn9spR++55aPLVqHUw4bmWyuo3AvmKzz91rZEej35v2Kb6p9LZ3a1p/21M89VDEVi0SgbNRxg5vrR9A1jTBi29k+nTilJaW0cpqwWLrHTZAfRWhb2qRh8d29KP6A2YcGMi2KzRpxxyADm57+1GRUYQGhA55RwD6llaB7XylX3GdxOFrRE4DUoNHtRHqfm9c=")
        print("boto3 configured successfully ...")
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        print("Key generated successfully ...")
        
        response = sns.list_subscriptions_by_topic(TopicArn="arn:aws:sns:us-east-1:119769868361:output_notification")
        subscriptions = response["Subscriptions"]
        print(subscriptions)
        keys = key.split(".")
        print('Filename: '+ keys[0])
        conn = pymysql.connect(host=rds_host, port=3306, user=name,
                               passwd=password, db=db_name)
        print('DB Connection successfull ...')
        query = "select * from detail where filename=\'" + keys[0] + "\.mp4';"
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query)
        print('Query executed successfully ...')
        email = ''
        for row in cur:
            email = row['email']
        print("Email: "+email)
        target_email = email
        message = "Hello,\n\nThanks for using SkimMeet application to get meeting insights.\nPlease find the below links to safely download the results\n\nAgenda and Conclusion: http://s3.amazonaws.com/skim-meeting-output2/" + \
                  keys[
                      0] + "\nMeeting cloud word: http://s3.amazonaws.com/skim-meeting-output1/" + key + "\n\nRegards,\nSkimMeet Team"
        for sub in subscriptions:
            if (sub['Endpoint'] == target_email):
                sns.publish(TopicArn="arn:aws:sns:us-east-1:119769868361:output_notification", Message=message,
                            Subject="SkimMeet Output", MessageStructure='string')
                print("Email sent successfully ...")
    except Exception as e:
        print("Database connection issue: Contact system administrator")
        sys.exit()
