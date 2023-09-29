import multiprocessing
import interpreter
import queue  # to handle the Empty exception from Queue.get_nowait()
import time
from typing import Callable, Dict, Tuple

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

def worker_process(input_queue: queue.Queue[str], result_queue: queue.Queue[Tuple[str, str]]) -> None:
    while True:
        while True:
            try:
                input_text = input_queue.get_nowait() #why can't I just use get()? dunno, but it hangs without nowait
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

                    result_queue.put((mode, data))
                    buffer = {}
            else:
                if len(buffer) != 1:
                    raise AssertionError(f"Expected buffer length to be 1, but got {buffer}")
                
                message = list(buffer.items())[0]
                mode, data = message

                result_queue.put((mode, data))
                buffer = {k: v}

        if buffer:
            message = list(buffer.items())[0]
            mode, data = message
            result_queue.put((mode, data))

        result_queue.put(("end_of_response", ""))

def result_listener(result_queue: queue.Queue[Tuple[str, str]]) -> None:
    while True:
        mode, data = result_queue.get()
        switch.get(mode, lambda data: print("ERROR: could not parse", data))(data)

def main() -> None:
    print('Welcome to unpaid intern! Send "reset" to reset the conversation.')
    print('%%END_OF_RESPONSE%%')

    result_queue: multiprocessing.Queue[Tuple[str, str]] = multiprocessing.Queue()
    input_queue: multiprocessing.Queue[str] = multiprocessing.Queue()

    # Start the worker process for the first time
    current_process = multiprocessing.Process(target=worker_process, args=(input_queue, result_queue))
    current_process.start()

    # Start the process listening to results
    multiprocessing.Process(target=result_listener, args=(result_queue,), daemon=True).start()

    while True:
        input_text = input()
        if input_text == "reset":
            if current_process and current_process.is_alive():
                current_process.terminate()
                current_process.join()
            
            # Start a new process after termination
            current_process = multiprocessing.Process(target=worker_process, args=(input_queue, result_queue))
            current_process.start()
            
            print("that intern has been fired :(")
            print('%%END_OF_RESPONSE%%')
        else:
            input_queue.put(input_text)
        
if __name__ == '__main__':
    main()