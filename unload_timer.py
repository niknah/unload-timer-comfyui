

import threading
import time
import logging
from aiohttp import web
from server import PromptServer
import execution
import folder_paths
from pathlib import Path
import json

def unload_models(unload_models):
    if unload_models:
        PromptServer.instance.prompt_queue.set_flag("unload_models", unload_models)
#    if free_memory:
#        PromptServer.instance.prompt_queue.set_flag("free_memory", free_memory)

next_idle = None
idle_secs = 60*15

is_stop_thread = False
my_thread = None
my_thread_sleep = None

def reset_idle_time():
    global next_idle
    next_idle = time.time() + idle_secs
    start()

def wake_thread_sleep():
    if my_thread_sleep:
        my_thread_sleep.set()

def set_idle_secs(secs):
    global idle_secs
    idle_secs = secs
    wake_thread_sleep()


def timer_thread():
    global next_idle
    global my_thread
    global my_thread_sleep

    while not is_stop_thread:
        if(PromptServer.instance.prompt_queue.get_tasks_remaining()==0):
            if next_idle is not None and time.time() >= next_idle:
                unload_models(True)
                next_idle = None
                logging.info("Unload timer: We have been idle. Auto unload VRAM.")
                # stop()
        else:
            reset_idle_time()
        
        if next_idle is not None:
            sleep_secs = next_idle - time.time()
        else:
            break
        logging.info(f"Unload timer: sleep: {sleep_secs}")

        my_thread_sleep = threading.Event()
        my_thread_sleep.wait(sleep_secs+2)
        # time.sleep(sleep_secs+2)
    my_thread = None

def start():
    global my_thread
    # global idle_secs
    global is_stop_thread

    if my_thread is not None:
        return

    # idle_secs = int(os.environ.get('COMFYUI_UNLOAD_VRAM_SECS', idle_secs))

    # 1. Create the thread, passing the function and arguments
    # Note: 'args' must be a tuple; use a trailing comma for a single argument
    my_thread = threading.Thread(target=timer_thread)

    is_stop_thread = False

    # 2. Start the thread execution
    my_thread.start()

    # 3. Wait for the thread to completely finish before moving the main script forward
    # my_thread.join()


def stop():
    global is_stop_thread
    is_stop_thread = True

def on_prompt(json_data):
    reset_idle_time()
    return json_data


old_task_done = None
def new_task_done(*args, **kwargs):
    reset_idle_time()
    return old_task_done(*args, **kwargs)


def init():
    global old_task_done
    old_task_done = execution.PromptQueue.task_done
    execution.PromptQueue.task_done = new_task_done

@PromptServer.instance.routes.post("/unload_timer/secs")
async def post_secs(request):
    # global idle_secs

    json_data = await request.json()
    set_idle_secs( json_data.get("secs", idle_secs))
    logging.info(f"UnloadTimer: Update idle secs: {idle_secs}")
    return web.json_response(
        {"ok":True},
        status=200
    )


def get_settings():
    # global idle_secs
    # ComfyUI serves user data assets through its internal file system API
    try:
        path = Path(folder_paths.get_user_directory()) / "default/comfy.settings.json"
        settings = json.loads(path.read_text(encoding="utf-8"))
        set_idle_secs( settings.get('UnloadTimer.Secs', idle_secs))
    except Exception:
        logging.exception("Unload Timer load settings error")

get_settings()


PromptServer.instance.add_on_prompt_handler(on_prompt)

