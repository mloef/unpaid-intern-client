import interpreter

switch = {
    "message": lambda data: print(data),
    "output": lambda data: print("```fix\n" + data + "\n```"),
    "code": lambda data: print("```\n" + data + "\n```"),
    "language": lambda data: print("`Running " + data + ":`"),
    "active_line": lambda data: None,#print("DEBUG: active_line", data),
    "executing": lambda data: None,#print("DEBUG: executing", data),
    "end_of_execution": lambda data: None,#print("DEBUG: end of execution:", data),
}

print('Welcome to unpaid intern! Send "reset" to reset the conversation.')
print('%%END_OF_RESPONSE%%')

while True:
    input_text = input()

    if input_text == "reset":
        interpreter.reset()
        print("the intern forgot everything :)")

    else:
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
            else:
                if len(buffer) != 1:
                    raise AssertionError(f"Expected buffer length to be 1, but got {buffer}")
                
                message = list(buffer.items())[0]
                mode, data = message

                switch.get(mode, lambda data: print("ERROR: could not parse", data))(data)
                buffer = {k: v}
        
        if len(buffer) != 1:
            raise AssertionError(f"Expected buffer length to be 1, but got {buffer}")
        message = list(buffer.items())[0]
        mode, data = message
        switch.get(mode, lambda data: print("ERROR: could not parse", data))(data)

    print('%%END_OF_RESPONSE%%')