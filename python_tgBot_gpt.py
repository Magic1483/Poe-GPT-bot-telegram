from telegram import Update , InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes,filters,MessageHandler
import poe
import peewee
from models import Person

# https://python-telegram-bot.org/
# https://github.com/python-telegram-bot/python-telegram-bot

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

# Poe version
async def PoePrompt(model,prompt,jailbreak):
  model_codename=language_models.get(model.lower())
  resp = ''
  client = poe.Client(tokens[current_token_index].replace('\n',''))

  #use jailbreak with ChatGPT
  if model == 'chatgpt' and jailbreak!='not':
       prompt = await request_with_jailbreak(jailbreak=jailbreak,prompt=prompt)
       print(f'request with JAILBREAK: {jailbreak}')
    
    
  for chunk in client.send_message(model_codename,prompt):
    resp+=chunk['text_new']
    
  
  return resp




async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')




async def handle_text(update,context):
    message_text =  update.message.text
    chat_id =  update.message.chat_id

    if message_text[0]!='/':
      global current_token_index
      p = Person.get_by_id(chat_id)
      print(message_text,p.model)
      try:
        resp = await PoePrompt(p.model,message_text,p.jailbreak_chat_gpt)
        print(message_text)
        await context.bot.send_message(chat_id=chat_id, text=resp)
      except RuntimeError:
        current_token_index+=1
        print('use next token')
        await handle_text(update,context)
        
      

async def change_model_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("Sage", callback_data="model#sage"),
            InlineKeyboardButton("ChatGPT", callback_data="model#chatgpt"),
            InlineKeyboardButton("GPT-4", callback_data="model#gpt-4"),
        ],
        [
          InlineKeyboardButton("Claude", callback_data="model#claude"),
          InlineKeyboardButton("Claude+", callback_data="model#claude+"),
          InlineKeyboardButton("Claude-instant-100k", callback_data="model#claude100k"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose GPT model:", reply_markup=reply_markup)

async def change_jailbreak_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("Not", callback_data="jailbreak#not"),
            InlineKeyboardButton("Dev mode v2", callback_data="jailbreak#dev_mode_v2"),
            InlineKeyboardButton("Dev mode + Ranti", callback_data="jailbreak#dev_mode_ranti"),
        ],
        [
          InlineKeyboardButton("AIM", callback_data="jailbreak#aim"),
          InlineKeyboardButton("DAN 6", callback_data="jailbreak#dan6"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose jailbreak for ChatGPT:", reply_markup=reply_markup)

async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
  chat_id =  update.message.chat_id
  try:
    p = Person.get(id=chat_id)
    await context.bot.send_message(chat_id=chat_id, text=f'user {chat_id}'+
                                  f'\nmodel: {p.model} \njailbreak Chat GPT: {p.jailbreak_chat_gpt} ')
  except:
    await context.bot.send_message(chat_id=chat_id, text='User not found')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE)-> None:
  chat_id =  update.message.chat_id
  await context.bot.send_message(chat_id=chat_id, text='Hacked gpt4 model and others!!\n[python-telegram-bot]')
  try:
    p = Person.get(id=int(chat_id))
    await context.bot.send_message(chat_id=chat_id, text=f'user {chat_id} exists ')
  except:
    Person.create(id=int(chat_id),model='sage',jailbreak_chat_gpt='not')
    await context.bot.send_message(chat_id=chat_id, text='User not found')
  
async def QueryHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    chat_id =  query.message.chat_id
  
    if query.data.startswith('model#'):
      print('change model')
      model = query.data.replace('model#','')
      res = await change_model(client=query.message.chat.id,model=model)
      if res:
        await context.bot.send_message(chat_id=chat_id, text=f'{chat_id} {model}')
    elif query.data.startswith('jailbreak#'):
      jailbreak = query.data.replace('jailbreak#','')
      res = await change_jailbreak(client=chat_id,jailbreak=jailbreak)
      print('change jailbreak')
      if res:
        await context.bot.send_message(chat_id=chat_id, text=f'{chat_id} {jailbreak}')
        

    
    # await query.answer()

    # await query.edit_message_text(text=f"Selected option: {query.data}")

async def change_model(client,model):
    print(client,model)
    # Update a person
    person = Person.get(Person.id == client)
    person.model = model
    person.save()
    return True

async def change_jailbreak(client,jailbreak):
    # Update a person
    person = Person.get(Person.id == client)
    person.jailbreak_chat_gpt = jailbreak
    person.save()
    return True


async def request_with_jailbreak(jailbreak,prompt):
   f = open(f'jailbreaks/'+jailbreak+'.txt', encoding='utf-8').readline()
   return f+prompt


app = ApplicationBuilder().token("bot-token").build()

app.add_handler(CommandHandler("change_model", change_model_handler))
app.add_handler(CommandHandler("change_jailbreak", change_jailbreak_handler))
app.add_handler(CommandHandler("profile", profile_handler))
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(QueryHandler))

app.add_handler(MessageHandler(filters.TEXT,handle_text))



app.run_polling()