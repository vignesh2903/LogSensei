import os
from openai import AzureOpenAI

azure_oai_endpoint = "https://logsensai-resource1.openai.azure.com/"
azure_oai_key = "a7f97c33a72b4003bc05daf741fe94fb"
azure_oai_deployment = "forthmodeldemo"


client = AzureOpenAI(azure_endpoint=azure_oai_endpoint, api_key=azure_oai_key, api_version="2023-05-15"
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
     "content": "{\n  \"query\": {\n    \"match\": {\n      \"Message\": \"ERROR\"\n    }\n  }\n}"}]

        # \"Can you search for ERROR in error log\"
print("\nSending request for summary to Azure OpenAI endpoint...\n\n")
completion = client.chat.completions.create(model=azure_oai_deployment,  # model = "deployment_name"
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