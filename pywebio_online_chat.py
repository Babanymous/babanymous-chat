import asyncio

from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import defer_call, info as session_info, run_async, run_js

chat_msgs = []
online_users = set()

MAX_MESSAGES_COUNT = 100

async def main():
    global chat_msgs
    
    put_markdown("## 🧊 Babanymous Chat\nonly 68 lines of code!")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    nickname = await input("#join_chat", required=True, placeholder="#your_name", validate=lambda n: "#this_name_already_exists!" if n in online_users or n == '📢' else None)
    online_users.add(nickname)

    chat_msgs.append(('📢', f'`{nickname}` joined_the_chat'))
    msg_box.append(put_markdown(f'📢 `{nickname}` joined_the_chat'))

    refresh_task = run_async(refresh_msg(nickname, msg_box))

    while True:
        data = await input_group("💭 new_message", [
            input(placeholder="#message_text ...", name="msg"),
            actions(name="cmd", buttons=["#send", {'label': "#leave", 'type': 'cancel'}])
        ], validate = lambda m: ('msg', "type_message_text") if m["cmd"] == "#send" and not m['msg'] else None)

        if data is None:
            break

        msg_box.append(put_markdown(f"`{nickname}`: {data['msg']}"))
        chat_msgs.append((nickname, data['msg']))

    refresh_task.close()

    online_users.remove(nickname)
    toast("#left_the_chat")
    msg_box.append(put_markdown(f'📢 user `{nickname}` left_the_chat'))
    chat_msgs.append(('📢', f'user `{nickname}` left_the_chat'))

    put_buttons(['#rejoin'], onclick=lambda btn:run_js('window.location.reload()'))

async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)
        
        for m in chat_msgs[last_idx:]:
            if m[0] != nickname: 
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))
        
        # remove expired
        if len(chat_msgs) > MAX_MESSAGES_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]
        
        last_idx = len(chat_msgs)

if __name__ == "__main__":
    start_server(main, debug=True, port=8080, cdn=False)