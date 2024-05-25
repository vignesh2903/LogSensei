import os
from openai import AzureOpenAI

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""

client = AzureOpenAI(
  azure_endpoint = "https://dev-mgmt-infra.amaiz.corp.amdocs.azr/v1/hackathon/regions/canadaeast/",
  api_key="5d57e861530c4f30b60dd25fae432f52",
  api_version="2023-05-15"
)

message_text = [{"role":"system","content":"You are an AI assistant that helps people find information."},{"role":"user","content":"HI"},{"role":"assistant","content":"Hello! How can I assist you today?"},{"role":"user","content":"What are logs"}]

completion = client.chat.completions.create(
  model="gpt-35", # model = "deployment_name"
  messages = message_text,
  temperature=0.7,
  max_tokens=800,
  top_p=0.95,
  frequency_penalty=0,
  presence_penalty=0,
  stop=None
)

es_query = completion.choices[0].message.content
print(es_query)