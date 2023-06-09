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
from Chimera import ChimeraPrompt,ChimeraImageGenerate




# Person.create_table()


language_models = {
  "sage": "capybara",
  "chatgpt": "chinchilla",
  "gpt-4": "beaver",
  "claude": "a2",
  "claude+": "a2_2",
  "claude100k": "a2_100k",
}

tokens = open('working.txt').readlines()
current_token_index = 0

api_id=123
api_hash =''
token =''

app = Client("bot2",api_id=api_id,api_hash=api_hash,bot_token=token)

# OFF/ON VOICE HANDLER
VOICE_INPUT_STATE = True
USE_CHIMERA_API = True


# Poe version
async def PoePrompt(prompt,model):
    resp =''
    try:
        client = poe.Client(tokens[current_token_index].replace('\n',''))
    except IndexError:
        print('No aviable tokens')
          
    for chunk in client.send_message(model,prompt):
        resp+=chunk['text_new']
        
    return resp
    # return resp

async def Prompt(send_to,model,prompt,jailbreak):
    model_codename=language_models.get(model.lower())

    #use jailbreak with ChatGPT
    if model == 'chatgpt' and jailbreak!='not':
        prompt = await request_with_jailbreak(jailbreak=jailbreak,prompt=prompt)
        print(f'request with JAILBREAK: {jailbreak}')

    if USE_CHIMERA_API:
        resp = await ChimeraPrompt(prompt,model)
    else:
        resp = await PoePrompt(prompt,model_codename)

    await app.send_message(send_to,resp)






@app.on_message(filters.command(["change_model"]))
async def change_model_command_handler(client, message):
   await client.send_message(chat_id=message.chat.id, reply_markup=InlineKeyboardMarkup(
      [
                    [  # First row
                        InlineKeyboardButton(  # Generates a callback query when pressed
                            "      Sage      ",
                            callback_data='model#sage'
                        ),
                        InlineKeyboardButton(  # Opens a web URL
                            "      ChatGPT      ",
                            callback_data='model#chatgpt'
                        ),
                        InlineKeyboardButton(  # Opens a web URL
                            "      GPT-4      ",
                            callback_data='model#gpt-4'
                        ),
                    ],
                    [  # Second row
                        InlineKeyboardButton(  # Opens the inline interface
                            "       Claude      ",
                            callback_data='model#claude'
                        ),
                        InlineKeyboardButton(  # Opens the inline interface in the current chat
                            "       Claude+     ",
                            callback_data='model#claude+'
                        ),
                        InlineKeyboardButton(  # Opens the inline interface in the current chat
                            "Claude-instant-100k",
                            callback_data='model#claude100k'
                        )
                    ]
        ]
   ),text='Change GPT model')

@app.on_message(filters.command(["change_jailbreak"]))#ONLY ChatGPT
async def change_jailbreak_handler(client, message):
   await client.send_message(chat_id=message.chat.id, reply_markup=InlineKeyboardMarkup(
      [
                    [  # First row
                        InlineKeyboardButton(  # Generates a callback query when pressed
                            "Not",
                            callback_data='jailbreak#not'
                        ),
                        InlineKeyboardButton(  
                            "Dev Mode v2",
                            callback_data='jailbreak#dev_mode_v2'
                        ),
                        InlineKeyboardButton(  
                            "DevMode + Ranti",
                            callback_data='jailbreak#dev_mode_ranti'
                        ),
                    ],
                    [
                       InlineKeyboardButton(  
                            "AIM",
                            callback_data='jailbreak#aim'
                        ),
                        InlineKeyboardButton(  
                            "DAN 6",
                            callback_data='jailbreak#dan6'
                        ),
                    ]
        ]
   ),text='Change jailbreak\nONLY ChatGPT')

@app.on_message(filters.command(["change_generate_type"]))#IMG or text
async def change_jailbreak_handler(client, message):
   await client.send_message(chat_id=message.chat.id, reply_markup=InlineKeyboardMarkup(
      [
                    [  # First row
                        InlineKeyboardButton(  # Generates a callback query when pressed
                            "Text",
                            callback_data='generate_type#text'
                        ),
                        InlineKeyboardButton(  
                            "IMG",
                            callback_data='generate_type#img'
                        ),
                    ]
        ]
   ),text='Change generate type\nimg or text.')

# define a callback handler to process user's response
@app.on_callback_query()
async def callback_handler(client, callback_query):
   if callback_query.data.startswith('model#'):
      print('change model')
      model = callback_query.data.replace('model#','')
      await change_model(client=callback_query.message.chat.id,model=model)
   elif callback_query.data.startswith('jailbreak#'):
      jailbreak = callback_query.data.replace('jailbreak#','')
      await change_jailbreak(client=callback_query.message.chat.id,jailbreak=jailbreak)
      print('change jailbreak')
   elif callback_query.data.startswith('generate_type#'):
      generate_type = callback_query.data.replace('generate_type#','')
      await change_generate_type(client=callback_query.message.chat.id,generate_type=generate_type)
    

@app.on_message(filters.command(["start"]))
async def start_command_handler(client, message):
    await client.send_message(chat_id=message.chat.id, text='Hacked gpt4 model and others!!')

    try:
        Person.get(id=int(message.chat.id))
        await client.send_message(chat_id=message.chat.id, text=f'user {message.chat.id} exists')
    except:
        Person.create(id=int(message.chat.id),model='sage',jailbreak_chat_gpt='not',generate_type='text')
        await client.send_message(chat_id=message.chat.id, text=f'user {message.chat.id} save')

    p1 = Person.select()
    for i in p1:
        print(i.id,i.model)

@app.on_message(filters.command(["profile"]))
async def profile_command_handler(client, message):
    

    try:
        p = Person.get(id=int(message.chat.id))
        await client.send_message(chat_id=message.chat.id, text=f'user {message.chat.id}'+
                                  f'\nmodel: {p.model} \njailbreak Chat GPT: {p.jailbreak_chat_gpt}\ngeneration_type: {p.generate_type} ')
    except:
        await client.send_message(chat_id=message.chat.id, text='User not found')



@app.on_message(filters.text & filters.private)
async def text_handler(client, message):
    p = Person.get_by_id(int(message.chat.id))

    if p.generate_type == 'text':
        if '/generate' in message.text:
            # p = Person.get_by_id(int(message.chat.id))
            prompt = message.text.split('/generate')[1]
            l = await ChimeraImageGenerate(prompt)
            print(prompt)
            for link in l:
                await app.send_photo(message.chat.id,link)
        elif message.text[0]!='/':
            global current_token_index
            
            print(message.text,p.model)

            

            try:
                await Prompt(message.chat.id,p.model,message.text,p.jailbreak_chat_gpt)
                print(message.text)
            except RuntimeError:
                current_token_index+=1
                print('use next token')
                await text_handler(client,message)
    elif p.generate_type == 'img':
        l = await ChimeraImageGenerate(message.text)
        for link in l:
            await app.send_photo(message.chat.id,link)

    


        
@app.on_message(filters.voice)
async def voice_handler(client,message):
    global VOICE_INPUT_STATE
    p = Person.get_by_id(int(message.chat.id))

    if VOICE_INPUT_STATE:
        
    #print(message)
        await app.download_media(message.voice.file_id,file_name='voice.ogg')
        global current_token_index
        text =  voice_decode()
            
        
        if p.generate_type == 'text':
            print(text,p.model)
            try:
                await Prompt(message.chat.id,p.model,text,p.jailbreak_chat_gpt)
                print(message.text)
            except RuntimeError:
                current_token_index+=1
                print('use next token')
                await voice_handler(client,message)
                    
        elif p.generate_type == 'img':
            print(text,' generate img')
            l = await ChimeraImageGenerate(text)
            for link in l:
                await app.send_photo(message.chat.id,link)
    else:
       await app.send_message(chat_id=message.chat.id,text='Voice input not aviable!!')
       
    



async def change_model(client,model):
    print(client,model)
    await app.send_message(chat_id=client, text=f'{client} {model}')
    # Update a person
    person = Person.get(Person.id == client)
    person.model = model
    person.save()

async def change_jailbreak(client,jailbreak):
    # Update a person
    person = Person.get(Person.id == client)
    person.jailbreak_chat_gpt = jailbreak
    person.save()
    await app.send_message(chat_id=client, text=f'{client} {person.jailbreak_chat_gpt}')

async def change_generate_type(client,generate_type):
    # Update a person
    person = Person.get(Person.id == client)
    person.generate_type = generate_type
    person.save()
    await app.send_message(chat_id=client, text=f'{client} generate_type is  {person.generate_type}')

async def request_with_jailbreak(jailbreak,prompt):
   f = open(f'jailbreaks/'+jailbreak+'.txt', encoding='utf-8').readline()
   return f+prompt


app.run()

