import multiprocessing
import interpreter

switch = {
    "message": lambda data: print(data),
    "output": lambda data: print("```fix\n" + data + "\n```"),
    "code": lambda data: print("```\n" + data + "\n```"),
    "language": lambda data: print("`Running " + data + ":`"),
    "active_line": lambda data: None,
    "executing": lambda data: None,
    "end_of_execution": lambda data: None
}

def process(input_text, result_queue):
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

print('Welcome to unpaid intern! Send "reset" to reset the conversation.')
print('%%END_OF_RESPONSE%%')

current_process = None
result_queue = multiprocessing.Queue()

while True:
    input_text = input()

    if input_text == "reset":
        if current_process and current_process.is_alive():
            current_process.terminate()
            current_process.join()  # wait for the process to truly terminate
        interpreter.reset()
        print("The intern forgot everything :)")
        print('%%END_OF_RESPONSE%%')
    else:
        # Starting the process
        current_process = multiprocessing.Process(target=process, args=(input_text, result_queue))
        current_process.start()

        # Wait for results and process them
        while current_process.is_alive() or not result_queue.empty():
            mode, data = result_queue.get()
            switch.get(mode, lambda data: print("ERROR: could not parse", data))(data)
        
        print('%%END_OF_RESPONSE%%')
