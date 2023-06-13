import openai
import asyncio

import aiohttp

openai.api_key = '--'
openai.api_base = "https://chimeragpt.adventblocks.cc/v1"


language_models = {
  "sage": "test-sage",
  "chatgpt": "gpt-3.5-turbo",
  "gpt-4": "gpt-4",
  "claude": "test-claude-instant",
  "claude+": "test-claude+",
  "claude100k": "test-claude-instant-100k",
}


async def ChimeraPrompt(text,model):
    response = openai.ChatCompletion.create(
        model=language_models[model],
        messages=[
            {'role': 'user', 'content': text},
        ],
        stream=True
    )

    res= ''

    for chunk in response:
        res+=chunk.choices[0].delta.get("content", "")
        # print(chunk.choices[0].delta.get("content", ""), end="", flush=True)
    
    print(res)
    return res

async def ChimeraImageGenerate(text):
    list = []
    response = openai.Image.create(
    prompt=text,
    n=2,  # images count
    )

    for i in response['data']:
        # print (i.url)
        list.append(i.url)

    return list

# asyncio.run( ChimeraImageGenerate('astronaut'))
