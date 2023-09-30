import multiprocessing
import queue  # to handle the Empty exception from Queue.get_nowait()
import threading
from typing import Callable, Dict, Tuple
import time

switch: Dict[str, Callable[[str], None]] = {
    "message": lambda data: print(data),
    "output": lambda data: print("```fix\n" + data + "\n```"),
    "code": lambda data: print("```\n" + data + "\n```"),
    "language": lambda data: print("`Running " + data + ":`"),
    "active_line": lambda data: None,
    "executing": lambda data: None,
    "end_of_execution": lambda data: None,
    "end_of_response": lambda data: print("%%END_OF_RESPONSE%%"),
}

def worker_process(input_queue: queue.Queue[str]) -> None:
    print('starting worker process')
    import interpreter #import starts the interpreter, so we only do it here so it only runs once

    while True:
        while True:
            try:
                #time.sleep(0.25)
                if not input_queue.empty():
                    print("found input at time", time.time())
                input_text = input_queue.get(timeout=1) #why can't I just use get()? dunno, but it hangs without nowait
                print('wtf')
                break
            except queue.Empty:
                pass
    
        buffer: Dict[str, str] = {}
        result = interpreter.chat(input_text, display=False, stream=True)
        
        for entry in result:
            if len(entry) != 1:
                raise AssertionError(f"Expected entry length to be 1, but got {entry}")

            k, v = list(entry.items())[0]
            if not buffer:
                buffer[k] = v
            elif buffer.get(k) and isinstance(v, str):
                buffer[k] += v
                if buffer[k][-1] == '\n':
                    if len(buffer) != 1:
                        raise AssertionError(f"Expected buffer length to be 1, but got {buffer}")
                    
                    mode = k
                    data = buffer[mode] + '** **'  # hack to preserve trailing \n in discord. doubles newline, though? why

                    switch.get(mode, lambda data: print("ERROR: could not parse", data))(data)
                    buffer = {}
            else:
                if len(buffer) != 1:
                    raise AssertionError(f"Expected buffer length to be 1, but got {buffer}")
                
                message = list(buffer.items())[0]
                mode, data = message

                switch.get(mode, lambda data: print("ERROR: could not parse", data))(data)
                buffer = {k: v}

        if buffer:
            message = list(buffer.items())[0]
            mode, data = message
            switch.get(mode, lambda data: print("ERROR: could not parse", data))(data)

        print('%%END_OF_RESPONSE%%')

def main() -> None:
    print('Welcome to unpaid intern! Send "reset" to reset the conversation.')
    print('%%END_OF_RESPONSE%%')

    input_queue: multiprocessing.Queue[str] = multiprocessing.Queue()

    # Start the worker process for the first time
    current_process = multiprocessing.Process(target=worker_process, args=(input_queue,))
    current_process.start()

    while True:
        input_text = input()
        if input_text == "reset":
            if current_process and current_process.is_alive():
                current_process.terminate()
                current_process.join()
            
            # Start a new process after termination
            current_process = multiprocessing.Process(target=worker_process, args=(input_queue,))
            current_process.start()
            
            print("that intern did not get a return offer :(")
            print('%%END_OF_RESPONSE%%')
        else:
            input_queue.put(input_text)
        
if __name__ == '__main__':
    main()