import urllib.parse
import boto3
import re
import codecs
print('Loading function')

s3 = boto3.resource('s3')

def lambda_handler(event, context):
    bucketName = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        data = s3.Object(bucketName, key)
        avoidWords = ['agenda', 'conclusion', 'start', 'stop', 'agenda.', 'conclusion.']
        line_stream = codecs.getreader("utf-8")
        agenda_start = "start agenda"
        agenda_end = "stop agenda"
        conclusion_start = "start conclusion"
        conclusion_end = "stop conclusion"
        agenda_start_flag = False
        agenda_end_flag = False
        conclusion_start_flag = False
        conclusion_end_flag = False
        avoid_agenda = False
        avoid_conclusion = False
        result = ''
        skip_flag = False
        stop_flag = False
        words = []

        for line in line_stream(data.get()['Body']):
            line_words = []
            line = line.lower()
            line_words = []
            line_words = line.split(" ")
            list_len = len(line_words)-1
            for i in range(list_len):
                print(i)
                print(line_words[i])
                if skip_flag == True:
                    skip_flag = False
                if 'start' in line_words[i]:
                    if 'agenda' in line_words[i+1]:
                        agenda_start_flag = True
                        result += "Agenda:\n"
                        skip_flag = True
                        print('Agenda started ...')
                    elif 'conclusion' in line_words[i+1]:
                        conclusion_start_flag = True
                        agenda_end_flag = True
                        skip_flag = True
                        print('Conclusion started ...')
                elif 'stop' in line_words[i]:
                    if 'agenda' in line_words[i+1]:
                        agenda_end_flag = True
                        result += '\n\n'+"Conclusion:\n"
                        skip_flag = True
                        print('Agenda ended ...')
                    elif 'conclusion' in line_words[i+1]:
                        conclusion_end_flag = True
                        skip_flag = True
                        print('Conclusion ended ...')
                elif (agenda_start_flag == True and agenda_end_flag == False and skip_flag == False) or (conclusion_start_flag == True and conclusion_end_flag == False and skip_flag==False):
                    result += line_words[i]
                    result += " "
            for word in line_words:
                if word not in avoidWords:
                    words.append(word)
            
        print('Writing to output files ...')
            
           
        print(result)
        newObject = s3.Object("skim-meeting-output2", key)
        newObject.put(Body=result)

        newObject2 = s3.Object("skim-meeting-words", key)
        result2 = ""
        for word in words:
            result2 += word + "\n"
        newObject2.put(Body=result2)

    except Exception as e:
        print(e)
        print(
            'Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(
                key, bucketName))
        raise e

