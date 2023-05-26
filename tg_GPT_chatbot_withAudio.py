import pyrogram
from pyrogram import Client,filters
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,InlineKeyboardButton)
import os
# import openai
import asyncio
import threading
import poe
from peewee import *
from models import Person
from voice_decode import voice_decode
# from webserver import keep_alive




# Person.create_table()


language_models = {
  "sage": "capybara",
  "chatgpt": "chinchilla",
  "gpt-4": "beaver",
  "claude": "a2",
  "claude+": "a2_2",
  "dragonfly": "Dragonfly",
}

tokens = open('working.txt').readlines()
current_token_index = 0

api_id=12345
api_hash ='--'
token ='--'

app = Client("bot2",api_id=api_id,api_hash=api_hash,bot_token=token)





# Poe version
async def PoePrompt(send_to,model,prompt):
  model_codename=language_models.get(model.lower())
  resp = ''
  client = poe.Client(tokens[current_token_index].replace('\n',''))
    
  for chunk in client.send_message(model_codename,prompt):
    resp+=chunk['text_new']
    
  await app.send_message(send_to,resp)
  # return resp





@app.on_message(filters.command(["change_model"]))
async def change_model_command_handler(client, message):
   await client.send_message(chat_id=message.chat.id, reply_markup=InlineKeyboardMarkup(
      [
                    [  # First row
                        InlineKeyboardButton(  # Generates a callback query when pressed
                            "Sage",
                            callback_data='sage'
                        ),
                        InlineKeyboardButton(  # Opens a web URL
                            "ChatGPT",
                            callback_data='chatgpt'
                        ),
                        InlineKeyboardButton(  # Opens a web URL
                            "GPT-4",
                            callback_data='gpt-4'
                        ),
                    ],
                    [  # Second row
                        InlineKeyboardButton(  # Opens the inline interface
                            "       Claude      ",
                            callback_data='claude'
                        ),
                        InlineKeyboardButton(  # Opens the inline interface in the current chat
                            "       Claude+     ",
                            callback_data='claude+'
                        ),
                        # InlineKeyboardButton(  # Opens the inline interface in the current chat
                        #     "Dragonfly",
                        #     callback_data='dragonfly'
                        # )
                    ]
        ]
   ),text='Change GPT model')

# define a callback handler to process user's response
@app.on_callback_query()
async def callback_handler(client, callback_query):
    await change_model(client=callback_query.message.chat.id,model=callback_query.data)
    

@app.on_message(filters.command(["start"]))
async def start_command_handler(client, message):
    await client.send_message(chat_id=message.chat.id, text='Hacked gpt4 model and others!!')

    try:
        Person.get(id=int(message.chat.id))
        await client.send_message(chat_id=message.chat.id, text=f'user {message.chat.id} exists')
    except:
        Person.create(id=int(message.chat.id),model='sage')
        await client.send_message(chat_id=message.chat.id, text=f'user {message.chat.id} save')

    p1 = Person.select()
    for i in p1:
        print(i.id,i.model)

@app.on_message(filters.text & filters.private)
async def text_handler(client, message):
  if message.text[0]!='/':
    global current_token_index
    p = Person.get_by_id(int(message.chat.id))
    print(message.text,p.model)

    try:
        await PoePrompt(message.chat.id,p.model,message.text)
        print(message.text)
    except RuntimeError:
        current_token_index+=1
        print('use next token')
        await text_handler(client,message)
        # await PoePrompt(message.chat.id,p.model,message.text)


        
@app.on_message(filters.voice)
async def voice_handler(client,message):
    #print(message)
    await app.download_media(message.voice.file_id,file_name='voice.ogg')
    global current_token_index
    text =  voice_decode()
    p = Person.get_by_id(int(message.chat.id))
    print(text,p.model)
    
    try:
        await PoePrompt(message.chat.id,p.model,text)
        print(message.text)
    except RuntimeError:
        current_token_index+=1
        print('use next token')
        await voice_handler(client,message)
    



async def change_model(client,model):
    print(client,model)
    await app.send_message(chat_id=client, text=f'{model} {client}')
    # Update a person
    person = Person.get(Person.id == client)
    person.model = model
    person.save()


app.run()

