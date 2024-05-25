    import os
    import httpx
    from langchain_openai import AzureChatOpenAI, ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.messages import HumanMessage

    azure_configs = {
        "azure_endpoint": "https://dev-mgmt-infra.amaiz.corp.amdocs.azr/v1/hackathon/regions/canadaeast/",
        "openai_api_version": "2023-05-15",
        "azure_deployment": "gpt-35",
        "openai_api_key": "5d57e861530c4f30b60dd25fae432f52",
        "openai_api_type": "azure",
        # "http_client": httpx.Client(verify=False)  # SSL Disabled
    }
    llm = AzureChatOpenAI(**azure_configs)

    result = llm([HumanMessage(content='Tell me about pluto')])
    print(result)

    # message_text = [{"role":"system","content":"You are an AI assistant that helps people find information."},{"role":"user","content":"HI"},{"role":"assistant","content":"Hello! How can I assist you today?"},{"role":"user","content":"What are logs"}]
    #
    # completion = llm.chat.completions.create(
    #     model="gpt-35-16k", # model = "deployment_name"
    #     messages = message_text,
    #     temperature=0.7,
    #     max_tokens=800,
    #     top_p=0.95,
    #     frequency_penalty=0,
    #     presence_penalty=0,
    #     stop=None
    # )
    #
    # es_query = completion.choices[0].message.content
    # print(es_query)