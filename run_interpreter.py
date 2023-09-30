import interpreter
from typing import Callable, Dict
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


def respond(input_text: str) -> None:
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
            if buffer[k][-1] == "\n":
                if len(buffer) != 1:
                    raise AssertionError(
                        f"Expected buffer length to be 1, but got {buffer}"
                    )

                mode = k
                data = (
                    buffer[mode] + "** **"
                )  # hack to preserve trailing \n in discord. doubles newline, though? why

                switch.get(mode, lambda data: print("ERROR: could not parse", data))(
                    data
                )
                buffer = {}
        else:
            if len(buffer) != 1:
                raise AssertionError(
                    f"Expected buffer length to be 1, but got {buffer}"
                )

            message = list(buffer.items())[0]
            mode, data = message

            switch.get(mode, lambda data: print("ERROR: could not parse", data))(data)
            buffer = {k: v}

    if buffer:
        message = list(buffer.items())[0]
        mode, data = message
        switch.get(mode, lambda data: print("ERROR: could not parse", data))(data)

    print("%%END_OF_RESPONSE%%")


def main() -> None:
    print('Welcome to unpaid intern! Send "reset" to interrupt the intern and reset the conversation.')
    print("%%END_OF_RESPONSE%%")

    while True:
        input_text = input()
        respond(input_text)


if __name__ == "__main__":
    main()