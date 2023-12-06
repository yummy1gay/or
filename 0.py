import asyncio
import time
from telethon.sync import TelegramClient, events
from telethon.tl import functions

API_ID = '9609511'
API_HASH = '066c47a00d147eb82ccd6af1f7bc7826'

session_names = ["sess1", "sess2", "sess3"]

async def vote_in_poll(session_name, poll_id, correct_option):
    try:
        client = TelegramClient(session_name, API_ID, API_HASH)
        await client.start()

        await client(functions.messages.SendVoteRequest(
            peer='pon4iik5',
            msg_id=poll_id,
            options=[str(correct_option - 1).encode()]
        ))
        await client.disconnect()
    except Exception as e:
        print(f"Error in session {session_name}: {e}")

async def process_poll(event):
    poll_id = event.id
    start_time = time.time()

    await event.client(functions.messages.SendVoteRequest(
        peer='pon4iik5',
        msg_id=poll_id,
        options=[b'0']
    ))

    updated_poll = await event.client.get_messages('pon4iik5', ids=[poll_id])
    correct_option = find_correct_option(updated_poll[0].poll.results.results)

    if correct_option:
        tasks = []
        for session_name in session_names:
            task = asyncio.ensure_future(vote_in_poll(session_name, poll_id, correct_option))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        end_time = time.time()
        duration = end_time - start_time
        print(f"All sessions voted in poll {poll_id}, correct option: {correct_option}")
        print(f"Voting took {duration} seconds")
        await event.reply(f'All sessions voted in poll {poll_id}, correct option: {correct_option}\nVoting took {duration} seconds')
    else:
        print(f"Poll {poll_id} has no correct option")

def find_correct_option(poll_results):
    for answer in poll_results:
        if answer.correct:
            return int(answer.option.decode()) + 1
    return None

if __name__ == "__main__":
    client = TelegramClient('helper_session', API_ID, API_HASH)
    client.start()
    client.add_event_handler(process_poll, events.NewMessage(chats=[-1001821572165], func=lambda e: e.poll is not None))
    client.run_until_disconnected()
