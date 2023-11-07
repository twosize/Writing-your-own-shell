import os
import sys

def main():
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        if prompt == "-":
            prompt = ""
    else:
        prompt = "jsh: "

    while True:

        if prompt:
            try:
                input_command = input(prompt)
            except EOFError:
                break
        else:
            input_command = input()

      
        cmd = input_command.split()

        if not cmd:
            continue
        
        if cmd[0] == "exit":
            break

      
        background = False
        if cmd[-1] == "&":
            cmd = cmd[:-1]
            background = True

        
        pid = os.fork()

        if pid == 0:
            try:
                os.execvp(cmd[0], cmd)
            except Exception as e:
                print(f"{cmd[0]}: {str(e)}")
                os._exit(1)

        elif pid > 0:
            if not background:
                os.wait()

        else:  
            print("Error: Fork failed!")

if __name__ == "__main__":
    main()
