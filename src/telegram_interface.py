"""
Copyright 2023 Carlos Ortiz Urshela

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
import sys

from   telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram     import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from   application import ailyn
from   interaction.context import InteractionContext


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger          = logging.getLogger(__name__)
telegram_params = dict(welcome_msg='',help_msg='')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user    = update.effective_user.name

    await update.message.reply_html(
        telegram_params['welcome_msg'],
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""

    await update.message.reply_html(
        telegram_params['help_msg'],
        reply_markup=ForceReply(selective=True),
    )

async def handle_text_interaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  '''default handler to deal with textual queries'''

  query      = update.message.text.strip()
  user_id    = update.effective_user.id
  user_name  = update.effective_user.full_name

  context  = InteractionContext(
     query          = query,
     source_id      = user_id,
     destination_id = '__LOCAL_BOT')
  
  answer = qa_pipeline.handle_query_interaction(context)
  await update.message.reply_html(
           answer, reply_markup=ForceReply(selective=True),
      )


async def audio_fn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   '''default handler to deal with voice note queries'''

   user_id    = update.effective_user.id

   audio_resource_info  = await context.bot.get_file(update.message.voice.file_id)
   audio_file_path      = audio_resource_info.file_path
   
   context  = InteractionContext(
             query          = '',
             source_id      = user_id,
             destination_id = '__LOCAL_BOT',
             audio_note_resorce_id = audio_file_path)
  
   answer = qa_pipeline.handle_query_interaction(context)
   await update.message.reply_html(
           answer, reply_markup=ForceReply(selective=True),
      )

def main():
   
   global qa_pipeline

   if len(sys.argv) >= 2:
      ailyn.load(sys.argv[1])
   else:
      #Looks up for the default env file 'env.txt' in the current path
      ailyn.load()  

   with open(ailyn._channels_env.welcome_filepath,encoding='utf-8') as wf:
      telegram_params['welcome_msg'] = wf.read()

   with open(ailyn._channels_env.help_filepath,encoding='utf-8') as hf:
      telegram_params['help_msg'] = hf.read()
   
   qa_pipeline = ailyn.new_qa_pipeline()
     
   application = Application.builder().token(ailyn._channels_env.telegram_bot_token).build() 

   application.add_handler(CommandHandler("start", start))
   application.add_handler(CommandHandler("help", help_command))
   application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                                     handle_text_interaction))
   application.add_handler(MessageHandler(filters.VOICE, audio_fn))

   # Run the bot until the user presses Ctrl-C
   application.run_polling()


if __name__ == "__main__":
    main()