import multiprocessing
import threading
import interpreter
import queue  # to handle the Empty exception from Queue.get_nowait()
import os

switch = {
    "message": lambda data: print(data),
    "output": lambda data: print("```fix\n" + data + "\n```"),
    "code": lambda data: print("```\n" + data + "\n```"),
    "language": lambda data: print("`Running " + data + ":`"),
    "active_line": lambda data: None,
    "executing": lambda data: None,
    "end_of_execution": lambda data: None,
    "end_of_response": lambda data: print("%%END_OF_RESPONSE%%"),
}

def worker_process(input_queue, result_queue):
    print('starting worker process')
    while True:
        input_text = input_queue.get()
        print('got input_text:', input_text)
    
        buffer = {}
        result = interpreter.chat(input_text, display=False, stream=True)
        
        for entry in result:
            if len(entry) != 1:
                raise AssertionError(f"Expected entry length to be 1, but got {entry}")

            k, v = list(entry.items())[0]
            if not buffer:
                buffer[k] = v
            elif buffer.get(k) and type(v) == str:
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

def result_listener(result_queue):
    while True:
        try:
            mode, data = result_queue.get_nowait()  # non-blocking get
            switch.get(mode, lambda data: print("ERROR: could not parse", data))(data)
        except queue.Empty:
            pass

def main():
    print('Welcome to unpaid intern! Send "reset" to reset the conversation.')
    print('%%END_OF_RESPONSE%%')

    current_process = None
    result_queue = multiprocessing.Queue()
    input_queue = multiprocessing.Queue()

    # Start the worker process for the first time
    current_process = multiprocessing.Process(target=worker_process, args=(input_queue, result_queue))
    current_process.start()

    # Start the process listening to results
    multiprocessing.Process(target=result_listener, args=(result_queue,), daemon=True).start()

    while True:
        input_text = input()
        print(input_queue.empty())
        if input_text == "reset":
            if current_process and current_process.is_alive():
                current_process.terminate()
                current_process.join()
                print("The intern was fired :(", current_process.is_alive())
            
            # Start a new process after termination
            current_process = multiprocessing.Process(target=worker_process, args=(input_queue, result_queue))
            current_process.start()
            
            print("The intern forgot everything :)")
            print('%%END_OF_RESPONSE%%')
        else:
            print('input:', input_text)
            print('current_process.is_alive():', current_process.is_alive())
            input_queue.put(input_text)
        
if __name__ == '__main__':
    main()