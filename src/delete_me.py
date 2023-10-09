from   interaction.context import InteractionContext
from   interaction.handlers.audio_handler import AudioHandler


query = "What's your name"
context = InteractionContext(query=query,
                                 source_id='source',
                                 destination_id='destination')

audioHandler           = AudioHandler()
audioHandler.handle(context)