import openai
import random
import json
from elasticsearch import Elasticsearch
import os
from werkzeug.utils import secure_filename
import re
import csv
import collections
from elasticsearch import Elasticsearch
from openai import OpenAI
from openai.lib.azure import AzureOpenAI
import os
# from openai import AsyncOpenAI
# Replace with your API key
import uuid
from elasticsearch import Elasticsearch
# Replace with your Elasticsearch credentials and host details
from flask import Flask, render_template, request, jsonify
import threading

app = Flask(__name__)
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
# Initialize variables for Elasticsearch and OpenAI clients
es = None
openai.api_key = None
azure_oai_endpoint = "https://dev-mgmt-infra.amaiz.corp.amdocs.azr/v1/hackathon/regions/canadaeast/"
azure_oai_key = "5d57e861530c4f30b60dd25fae432f52"


@app.route('/clear_data', methods=['POST'])
def clear_data():
    # Retrieve the log level from the AJAX request
    index = "aisensei4"
    es_host = "10.69.55.11"
    es_port = 31020
    es_username = "elastic"
    es_password = "elastic_password"
    es = Elasticsearch(
        [{"host": es_host, "port": es_port, "scheme": "https"}],
        http_auth=(es_username, es_password),
        verify_certs=False
    )
    fileName = request.form['fileName']
    print(fileName)
    # uploade
    query = {"query": {"match": {"fileName": fileName}}}
    res = es.delete_by_query(index=index, body=query)
    myfile = "uploadFile/" + fileName
    # If file exists, delete it.
    if os.path.isfile(myfile):
        os.remove(myfile)
    else:
        # If it fails, inform the user.
        print("Error: %s file not found" % myfile)
    # Process the log level (you can save it to a database, log it, etc.)
    # For now, let's just return it as a response
    return "Session is clear"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/config', methods=['POST'])
def config():
    global es, openai
    openai.api_key = request.form['openai_key']
    es_host = "10.69.55.11"
    es_port = 31020
    es_username = "elastic"
    es_password = "elastic_password"
    es = Elasticsearch(
        [{"host": es_host, "port": es_port, "scheme": "https"}],
        http_auth=(es_username, es_password),
        verify_certs=False
    )
    return jsonify({'success': True})


@app.route('/message', methods=['POST'])
def message():
    if not es or not openai.api_key:
        return jsonify(
            {'error': 'Configuration is missing. Please provide the OpenAI API key and Elasticsearch details.'}), 400
    user_input = request.form['user_input']
    response = elastic_request_create(user_input)
    return jsonify({'response': response})


@app.route('/loglevel', methods=['POST'])
def get_log_level():
    # Retrieve the log level from the AJAX request
    log_level = request.form['logLevel']
    # Process the log level (you can save it to a database, log it, etc.)
    # For now, let's just return it as a response
    return log_level


def elastic_request_create(user_input):
    es_host = "https://10.69.55.11:31020"
    es_port = 31020
    es_username = "elastic"
    es_password = "elastic_password"
    index = "aisensei"
    body = {
        "query": {
            "match": {
                "logs": user_input
            }
        }
    }
    search_results = es.search(index=index, body=body)
    result = []
    i = 0
    print(len(search_results["hits"]["hits"]))
    while (i < len(search_results["hits"]["hits"])):
        print(search_results["hits"]["hits"][i]["_source"]["logs"])
        result.append(search_results["hits"]["hits"][i]["_source"]["logs"])
        i = i + 1

    print(len(result))
    print(result)
    return result


app.config['UPLOAD_FOLDER'] = 'uploadfile'


@app.route('/check_upload', methods=['POST'])
def check_upload():
    try:
        print("test")
        uploaded_file = request.files['filename']
        if uploaded_file:
            # Save the file to the specified folder
            filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(filename)
            # print(upload_file, "",filename)
            write_to_csv(count_ip(log_file_reader(filename)), uploaded_file.filename)
            return {"fileName": uploaded_file.filename, "message": "File uploaded successfully!"}
        else:
            return "File upload failed."
    except Exception as e:
        return str(e)


"""
Sample log file parser which will parse the log file, get the IP addressed with their count frequency and export the data to a csv file
"""


def read_json_objects(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
        json_objects = data.strip().split('\n')
        parsed_objects = [json.loads(obj) for obj in json_objects]
    return parsed_objects


def log_file_reader(filename):
    # Get all IP addresses from the log file
    with open(filename) as f:
        log = f.read()
        regex = r'\{\s*"Timestamp"\s*:\s*"[^"]*"\s*,\s*"RequestID"\s*:\s*"[^"]*"\s*,\s*"Severity"\s*:\s*"[^"]*"\s*,\s*"TID"\s*:\s*"[^"]*"\s*,\s*"SpanID"\s*:\s*"[^"]*"\s*,\s*"Tenant"\s*:\s*"[^"]*"\s*,\s*"MessageCode"\s*:\s*"[^"]*"\s*,\s*"Class"\s*:\s*"[^"]*"\s*,\s*"Message"\s*:\s*"[^"]*"\s*,\s*"StackTrace"\s*:\s*"[^"]*"\s*,\s*"Component"\s*:\s*"[^"]*"\s*,\s*"SubComponent"\s*:\s*"[^"]*"\s*,\s*"ContainerID"\s*:\s*"[^"]*"\s*,\s*"HostID"\s*:\s*"[^"]*"\s*,\s*"ComponentVersion"\s*:\s*"[^"]*"\s*\}'
        ip_list = re.findall(regex, log)
        return ip_list


# Get total count of IPs
def count_ip(ip_list):
    return collections.Counter(ip_list)


def write_to_csv(counter, fileName):
    for item in counter:
        print(item)
        store_elastic_search(item, fileName)


def store_elastic_search(item, fileName):
    index = "aisensei4"
    es_host = "10.69.55.11"
    es_port = 31020
    es_username = "elastic"
    es_password = "elastic_password"
    es = Elasticsearch(
        [{"host": es_host, "port": es_port, "scheme": "https"}],
        http_auth=(es_username, es_password),
        verify_certs=False
    )
    print("====item", item)
    parsed_objects = json.loads(item)
    print("=====", parsed_objects)
    print(item)
    data_to_index = parsed_objects
    data_to_index['fileName'] = fileName
    print(data_to_index)
    # Index the data
    es.index(index=index, body=data_to_index)


@app.route("/save_query", methods=["POST"])
def save_query():
    try:
        data = request.form.get("query")  # Get the query from the form
        # Save the query to a file or database
        # Example: write to a text file
        print("data saved is :" + data)
        uploaded_file = request.form['fileName']
        print(uploaded_file)
        prompt = data + "and fileName is " + uploaded_file
        log_level = get_log_level()
        print(log_level)
        if (log_level == "General Logs"):
            return query_to_esQuery(prompt)
        elif (log_level == "GC Logs"):
            return query_to_esQuery_Garbage(prompt)
        elif (log_level == "Thread Dump"):
            return query_to_esQuery_ThreadDump(prompt)
        # query_to_esQuery(data)
        # return "Query saved successfully!"
    except Exception as e:
        return str(e), 500


@app.route("/save_query2", methods=["POST"])
def save_query2():
    try:
        data = request.form.get("query")  # Get the query from the form
        # Save the query to a file or database
        # Example: write to a text file
        chatId = request.form.get("chatId")
        print("data saved is :" + data)
        # print("Random UUID using uuid1():", uuid.uuid1())
        # query_to_esQuery(data)
        if not chatId:
            chatId = uuid.uuid1()
        result = {"chatId": chatId, "result": "Query saved successfully!, es query result"}
        print("result ===", result)
        uploaded_file = request.form['fileName']
        # prompt= data+"and fileName is"+uploaded_file
        # return query_to_esQuery(prompt)
        print(es_filtered_data)
        return {"chatId": chatId, "result": es_to_opeAi(es_filtered_data, data)}
        # query_to_esQuery(data)
        # return "Query saved successfully!"
    except Exception as e:
        return str(e), 500


def query_to_esQuery(data):
    try:
        # Get configuration settings
        client = AzureOpenAI(
            azure_endpoint=azure_oai_endpoint,
            api_key=azure_oai_key,
            api_version="2023-05-15"
        )
        # Send request to Azure OpenAI model
        message_text = [
            {"role": "system",
             "content": "You are an AI assistant that helps people to create Elastic Search query. The data is stored in index named aisensei"},
            {"role": "user", "content": "Can you search for Batch loading started for batch request id in warn log"},
            {"role": "assistant",
             "content": "{\n  \"query\": {\n    \"match\": {\n      \"Message\": \"Batch loading started for batch request id in warn log\"\n    }\n  }\n}"},
            {"role": "user", "content": "Give me count of all errors"},
            {"role": "assistant",
             "content": "{\n\"query\": {\n\"match\": {\n\"Severity\": \"error\"\n}\n},\n\"size\": 0,\n\"aggs\": {\n\"error_count\": {\n\"value_count\": {\n\"field\": \"Severity\"\n}\n}\n}\n}"},
            {"role": "user", "content": "Give me the logs of last 24 hours"},
            {"role": "assistant",
             "content": "{\n\"query\": {\n\"range\": {\n\"@timestamp\": {\n\"gte\": \"now-24h\",\n\"lte\": \"now\"\n}\n}\n}\n}"},
            {"role": "user", "content": "Give me all logs for API starts with findcrosscontext"},
            {"role": "assistant",
             "content": "{\n\"query\": {\n\"wildcard\": {\n\"Message\": \"findcrosscontext*\"\n}\n}\n}"},
            {"role": "user", "content": "Give me the logs of last 24 hours"},
            {"role": "assistant",
             "content": "{\n\"query\": {\n\"range\": {\n\"Timestamp\": {\n\"gte\": \"now-24h\",\n\"lte\": \"now\"\n}\n}\n}"},
            {"role": "user",
             "content": data}]
        # \"Can you search for ERROR in error log\"
        print("\nSending request for summary to Azure OpenAI endpoint...\n\n")
        completion = client.chat.completions.create(
            model="gpt-35",  # model = "deployment_name"
            messages=message_text,
            temperature=0.0,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        es_query = completion.choices[0].message.content
        print(es_query)
        filtered_data_es = query_elastic_search(es_query)
        chunk_size = 1500
        chunks = split_string(filtered_data_es, chunk_size)
        # for chunk in chunks:
        #     print(chunk)
        print(type(chunks))
        global es_filtered_data
        es_filtered_data = str(chunks[-1])
        return es_to_opeAi(str(chunks[-1]), data)
    except Exception as ex:
        print(ex)


es_filtered_data = []


def query_to_esQuery_ThreadDump(data):
    try:
        # Get configuration settings
        azure_oai_deployment = "gpt-35"
        client = AzureOpenAI(
            azure_endpoint=azure_oai_endpoint,
            api_key=azure_oai_key,
            api_version="2023-05-15"
        )
        # Send request to Azure OpenAI model
        message_text = [{"role": "system",
                         "content": "you are a smart ai that can create elastic search query from this sentence that will search in elastic search containing thread dump logs , the dump displays the list of threads. Each elastic search record contains the following information of a thread: Name: it can provide useful information if developers include a meaningful thread name Priority (prior): the priority of the thread Java ID (tid): the unique ID given by the JVM Native ID (nid): the unique ID given by the OS, useful to extract correlation with CPU or memory processing State: the actual state of the thread Stack trace: the most important source of information to decipher what is happening with our application Thread States could be RUNNABLE, BLOCKED,TIMED_WAITING . all the data is stored in only one attributes thread-record as text format"},
                        {"role": "user", "content": "Analyze the log for thread Catalina-utility-1"},
                        {"role": "assistant",
                         "content": "{  \n  \"query\": {  \n    \"match_phrase\": {  \n      \"thread-record\": \"Catalina-utility-1\"  \n    }  \n  }  \n} "},
                        {"role": "user", "content": "give all thread in WAITING"}, {"role": "assistant","content": "{\n\"query\": {\n\"match\": {\n\"thread-record\": \"WAITING\"\n}\n}\n}"}
                        {"role": "user", "content": data}]
        # \"Can you search for ERROR in error log\"
        print("\nSending request for summary to Azure OpenAI endpoint...\n\n")
        completion = client.chat.completions.create(
            model=azure_oai_deployment,  # model = "deployment_name"
            messages=message_text,
            temperature=0.0,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        es_query = completion.choices[0].message.content
        print(es_query)
        filtered_data_es = query_elastic_search(es_query)
        chunk_size = 1500
        chunks = split_string(filtered_data_es, chunk_size)
        # for chunk in chunks:
        #     print(chunk)
        print(type(chunks))
        return es_to_opeAi(str(chunks[-1]), data)
    except Exception as ex:
        print(ex)


def query_to_esQuery_Garbage(data):
    try:
        # Get configuration settings
        azure_oai_deployment = "forthmodeldemo"
        client = AzureOpenAI(
            azure_endpoint=azure_oai_endpoint,
            api_key=azure_oai_key,
            api_version="2023-05-15"
        )
        # Send request to Azure OpenAI model
        message_text = [
            {"role": "system", "content": "You are an AI assistant that helps to generate Elasticsearch query."},
            {"role": "user",
             "content": "\"please search errors in logs regarding find cross context \" , create elastic search query from this sentence that will search in elastic search containing application log"},
            {"role": "assistant",
             "content": "GET /your_index/_search\n{\n  \"query\": {\n    \"bool\": {\n      \"must\": [\n        {\n          \"match\": {\n            \"log_message\": \"error\"\n          }\n        },\n        {\n          \"match_phrase\": {\n            \"log_message\": \"find cross context\"\n          }\n        }\n      ]\n    }\n  }\n}"},
            {"role": "user",
             "content": "\"please give count of find cross context\" create elastic search query from this sentence that will search in elastic search containing application log"},
            {"role": "assistant",
             "content": "GET /your_index/_count\n{\n  \"query\": {\n    \"match_phrase\": {\n      \"log_message\": \"find cross context\"\n    }\n  }\n}"},
            {"role": "user",
             "content": "\"please give count of find cross context\" create elastic search query from this sentence that will search in elastic search containing application log in index \"aisensei\""},
            {"role": "assistant",
             "content": "GET /aisensei/_count\n{\n  \"query\": {\n    \"match_phrase\": {\n      \"log_message\": \"find cross context\"\n    }\n  }\n}"},
            {"role": "user",
             "content": "\"please give count of find cross context\" create elastic search query from this sentence that will search in elastic search containing application log in index \"aisensei\" and logs"},
            {"role": "assistant",
             "content": "{\n  \"query\": {\n    \"bool\": {\n      \"should\": [\n        {\n          \"match_phrase\": {\n            \"log_message\": \"find cross context\"\n          }\n        },\n        {\n          \"match_phrase\": {\n            \"logs\": \"find cross context\"\n          }\n        }\n      ]\n    }\n  }\n}"},
            {"role": "user",
             "content": "\"count of logs very hour between 2024-01-0914:24:48 and 2024-02-0914:35:43\". create elastic search query from this sentence that will search in elastic search containing application log in index \"aisensei\" , logs are store in below json format {\"Timestamp\":\"\",\"RequestID\":\"\",\"Severity\":\"\",\"TID\":\"\",\"SpanID\":\"\",\"Tenant\":\"\",\"MessageCode\":\"\",\"Class\":\"\",\"Message\":\"\",\"StackTrace\":\"\",\"Component\":\"\",\"SubComponent\":\"\",\"ContainerID\":\"\",\"HostID\":\"\",\"ComponentVersion\":\"\"}"},
            {"role": "assistant",
             "content": "{\n  \"size\": 0,\n  \"query\": {\n    \"bool\": {\n      \"must\": [\n        {\n          \"range\": {\n            \"Timestamp\": {\n              \"gte\": \"2024-01-09T14:24:48\",\n              \"lte\": \"2024-02-09T14:35:43\"\n            }\n          }\n        }\n      ]\n    }\n  },\n  \"aggs\": {\n    \"logs_per_hour\": {\n      \"date_histogram\": {\n        \"field\": \"Timestamp\",\n        \"fixed_interval\": \"1h\"\n      }\n    }\n  }\n}"},
            {"role": "user",
             "content": "\"give me the total kafka commit\" create elastic search query from this sentence that will search in elastic search containing application log in index \"aisensei\" , logs are store in below json format {\"Timestamp\":\"\",\"RequestID\":\"\",\"Severity\":\"\",\"TID\":\"\",\"SpanID\":\"\",\"Tenant\":\"\",\"MessageCode\":\"\",\"Class\":\"\",\"Message\":\"\",\"StackTrace\":\"\",\"Component\":\"\",\"SubComponent\":\"\",\"ContainerID\":\"\",\"HostID\":\"\",\"ComponentVersion\":\"\"}"},
            {"role": "assistant",
             "content": "{\n  \"size\": 0,\n  \"query\": {\n    \"match\": {\n      \"Message\": \"kafka commit\"\n    }\n  }\n}"},
            {"role": "user", "content": "Give me all the error logs"}, {"role": "assistant",
                                                                        "content": "{\n  \"query\": {\n    \"match\": {\n      \"Severity\": \"error\"\n    }\n  }\n}"},
            {"role": "user",
             "content": "\"give me all the error logs\". create elastic search query from this sentence that will search in elastic search containing application log in index \"aisensei\" , logs are store in below json format"},
            {"role": "assistant",
             "content": "{\n  \"query\": {\n    \"match\": {\n      \"Severity\": \"error\"\n    }\n  }\n}"},
            {"role": "user",
             "content": "\"Can you search for ERROR in error log\" create elastic search query from this sentence that will search in elastic search containing application log in index \"aisensei\" , logs are store in below json format {\"Timestamp\":\"\",\"RequestID\":\"\",\"Severity\":\"\",\"TID\":\"\",\"SpanID\":\"\",\"Tenant\":\"\",\"MessageCode\":\"\",\"Class\":\"\",\"Message\":\"\",\"StackTrace\":\"\",\"Component\":\"\",\"SubComponent\":\"\",\"ContainerID\":\"\",\"HostID\":\"\",\"ComponentVersion\":\"\"}"},
            {"role": "assistant",
             "content": "{\n  \"query\": {\n    \"match\": {\n      \"Message\": \"ERROR\"\n    }\n  }\n}"},
            {"role": "user",
             "content": "\"" + data + "\"" + "create elastic search query from this sentence that will search in elastic search containing application log in index \"aisensei\" , logs are store in below json format {\"Timestamp\":\"\",\"RequestID\":\"\",\"Severity\":\"\",\"TID\":\"\",\"SpanID\":\"\",\"Tenant\":\"\",\"MessageCode\":\"\",\"Class\":\"\",\"Message\":\"\",\"StackTrace\":\"\",\"Component\":\"\",\"SubComponent\":\"\",\"ContainerID\":\"\",\"HostID\":\"\",\"ComponentVersion\":\"\"}"}]
        # \"Can you search for ERROR in error log\"
        print("\nSending request for summary to Azure OpenAI endpoint...\n\n")
        completion = client.chat.completions.create(
            model=azure_oai_deployment,  # model = "deployment_name"
            messages=message_text,
            temperature=0.0,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        es_query = completion.choices[0].message.content
        print(es_query)
        filtered_data_es = query_elastic_search(es_query)
        chunk_size = 1500
        chunks = split_string(filtered_data_es, chunk_size)
        # for chunk in chunks:
        #     print(chunk)
        print(type(chunks))
        return es_to_opeAi(str(chunks[-1]), data)
    except Exception as ex:
        print(ex)


def es_to_opeAi(data, prompt):
    try:

        # Read text from file
        # text = open(file="text.txt", encoding="utf8").read()
        print("\nSending request for summary to Azure OpenAI endpoint...\n\n")
        # Add code to build request...
        client = AzureOpenAI(
            azure_endpoint=azure_oai_endpoint,
            api_key=azure_oai_key,
            api_version="2023-05-15"
        )
        # Send request to Azure OpenAI model
        response = client.chat.completions.create(
            model="gpt-35",
            temperature=0.0,
            max_tokens=2000,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": data + prompt}
            ]
        )
        print("Summary: " + response.choices[0].message.content + "\n")
        return response.choices[0].message.content;
    except Exception as ex:
        print(ex)


def query_elastic_search(es_query):
    index = "aisensei4"
    es_host = "10.69.55.11"
    es_port = 31020
    es_username = "elastic"
    es_password = "elastic_password"
    es = Elasticsearch(
        [{"host": es_host, "port": es_port, "scheme": "https"}],
        http_auth=(es_username, es_password),
        verify_certs=False
    )
    #  body = {
    #     "query":{
    #         "match":{
    #         "logs": user_input
    #         }
    #     }
    # }
    search_results = es.search(index=index, body=es_query)
    print(len(search_results), search_results)
    result = []
    i = 0
    print(len(search_results["hits"]["hits"]))
    while (i < len(search_results["hits"]["hits"])):
        print(search_results["hits"]["hits"][i]["_source"])
        result.append(search_results["hits"]["hits"][i]["_source"])
        i = i + 1
    print(len(result))
    print(result)
    return result


def openaiquery(result):
    chunk_size = 1500
    chunks = split_string(result, chunk_size)
    for chunk in chunks:
        print(chunk)
        # main(chunk)


def split_string(string, chunk_size):
    return [string[i:i + chunk_size] for i in range(0, len(string), chunk_size)]


# def multiple_es_query():

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)