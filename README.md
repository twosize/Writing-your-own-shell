# Writing-your-own-shell
Writing a shell in python
For this assignment, you will be writing a primitive shell program. This program will prompt the user to give a program name and optional arguments, and will launch that program with those arguments, optionally in the background (if the user puts "&" at the end of a command line). Your shell will not implement changing directories; that is, "cd somedir" will not work.

Specifications
This shell should take one optional command line argument, which is its prompt. If no argument is given, the prompt should be "jsh: ". If the argument is "-", then do not print any prompt.
I'll call this shell program you'll be writing "jsh." Jsh reads lines from standard input, and if they are non-blank, it attempts to execute them. Like the shell, jsh should search the PATH variable to find executable files specified as relative path names (this is the natural behavior of execvp()). If a command line ends with an ampersand (&), then jsh should not wait for the command to finish before returning the prompt. Otherwise, it should wait for the command to finish.
Do not let zombies exist longer than necessary. (Use wait(), not waitpid().)
If a user command fails, print an error message for the user that is equivalent to what happens if you call perror(cmd[0]) in C.
Jsh should exit when the user types CNTL-D or exit. (Exit is the only built-in command your shell is implementing.)
Languages: You may use C, C++, or Python. If in doubt, I recommend Python first, C++ second, and C last. Even if you don't know Python, it's so easy that it will probably take you less time to learn Python from scratch than it will be to do this in C if you don't have a decent grasp of C.
Libraries: Here's what you're allowed to use outside the base language:
C/C++: When you need to make system calls, you should be using the POSIX C API. That is, stuff like "#include <unistd.h>" and "#include <sys/wait.h>". The system calls you need are _exit(), fork(), execvp(), and wait().
Python: You should use the os module, which includes os._exit(), os.fork(), os.execvp(), and os.wait(). You will also need the sys module for argv. You may not use any other module, especially not the subprocess module. (Note: os.wait() returns a tuple of the child pid and its exit statusLinks to an external site., so you'll want something like "pid, _ = os.wait()")
Product: You should turn in a single file containing your code. The extension should be ".py", ".cpp", or ".c". No separate headers or non-standard libraries. Please name your file according to your first initial and last name; e.g., "jsmith.py". I should be able to run your code as follows from a command line:
C: "gcc jsmith.c", followed by "./a.out".
C++: "g++ jsmith.cpp", followed by "./a.out".
Python: "python jsmith.py"
Extra info:
Technically, the above is all you need. The whole rest of this document is to help you. The above is the whole assignment. Everything else is extra tips and hints.
The main specifications are taken from "Part 1" of this write-upLinks to an external site.. (It's from the professor who taught me this stuff at UTK. "jsh" refers to your program.) It's also very similar to parts I and II of programming project 1 at the end of Chapter 3 of our textbook.
High-level strategy
Check if there are any words at all in the line of user input... if not, just move on to the next iteration of the outer loop.
Split each line of user input to whitespace-separated words, putting them in the appropriate structure that execvp() needs: Either a friendly Python list of friendly Python strings, or an ugly (NULL-terminated) C-style array of ugly C-style strings.
But along the way, you'll need to check if the last word on the user's line is an ampersand ("&"). If so, don't put the ampersand itself on the list/array of words. Just set some flag (boolean variable) to remind yourself later that the user is requesting that something be run in the background.
You may find it helpful to start by just focusing on getting this outer loop working and getting user input split into separate words. I've written this up as an optional separate first step for you, with hints and advice, in this page.
Each time you go through the loop, you'll be printing a prompt string for your user, and what this string is is based on the command-line arguments your user included when they started your shell program. You may find it helpful to get this working as a separate step. I've written it up that way, with hints and such, in this page.
Call fork(), saving its return value.
Check the return value of fork() to see if you're now the child or if you're now the parent.
If you're the child:
Make the appropriate execvp() call. Execvp() needs two arguments. The first is a single string containing the name of the executable program that should be run. The second is that whole list of words you created earlier; this is what the new process will see as its argv[] array. (Note that the first element of this list will be the same word as the first argument to execvp(), which feels a little weird at first, but that's the right way to do it here.)
execvp() should not return. If it did return, something went wrong, and you want to do two things:
Print a helpful error message for the user.
Much more importantly, call _exit(1)! As we have discussed, failing to do this can create a fork bomb.
If you're the parent:
If no ampersand was given, wait() for the child. But you can't simply call wait(), because other children that were run in the background earlier might return first, and in that case you need to keep waiting until you get back the child you just created. So call wait() in a loop, and the loop ends once the return value of the wait() call matches the pid of the child you just forked off.
If an ampersand was given, no need to do anything; just continue on to the next iteration.
How to get strings into the right format for execvp():
If you don't like the look of the rest of this section, just switch to Python, where the .split() method gives you a friendly Python list, which is what os.execvp() takes as its second argument. (First argument, of course, is just a Python string.)
C++: Might as well keep things as C++-ish as possible for as long as you can:
If you've been putting the user's line into a std::istringstream and then using the >> operator to extract each word and then print it, you can basically do the same thing, except load those std::string's into a std::vector instead of printing them. You could use std::vector::push_back(), for example.
But you'll still need to get this data into ugly C form; skip to the "Both C and C++" section below.
C: You've probably been using strtok() or strtok_r(). Keep using that. Now you also have to get those strings into a C-style array. Well, C-style arrays have static length, so you can't simply put an arbitrary number of things on one. You have a few options:
Just allocate a big array and hope it's big enough. If you go this route, my suggestion is don't mess around trying to save memory. I'd make it big enough for 256, 512, or 1024 words.
Use realloc() to re-allocate your array as it grows.
Make two passes through the input line: The first pass to count words, then use calloc() to allocate an array of the right size, and then a second pass to actually extract the words and copy them into the array.
Both C and C++:
Remember to allocate one extra space in your C-style array of strings, because the last element needs to be a NULL pointer. That's how execvp() is going to know where the end of the array is.
Whether you're coming from a C++ std::vector of std::strings, or from a strtok() loop in C, you'll probably want to use strdup() to get C-style strings into the C-style array. If using C++, remember that std::string::c_str() gives you access to the underlying C-style string.
Remember to call free() on anything you allocate with calloc(), strdup(), etc.
Flushing output buffers:
Flushing a buffer means to empty it by doing what you ultimately need to do with it. For efficiency, the runtime system normally saves up output and only writes it to the terminal occasionally, or when it figures out that it's needed. Sometimes if you use different styles of I/O, like from different parts of the standard library, the runtime system gets confused about when it needs to flush the buffer, so you need to tell it explicitly. Here's how to do it if you need it:
Python: add "flush=True" to print(); e.g., print(prompt, end="", flush=True)
C++: std::cout << std::flush;
C: fflush(stdout);
Error message for failed execvp() calls:
Python: The data you need is in the exception that gets raised when execvp fails, so you'll need something like this:
        try:
            os.execvp(cmd[0], cmd)
        except os.error as e:
            print(f'{cmd[0]}: {e.strerror}')
C/C++: After execvp(), call perror(cmd[0]);
Either way, remember to call os._exit(1) or _exit(1) after this!
Reference binary
Here is a linkLinks to an external site. to a reference binary that does what your program should do. This reference program also implements fancy things like file redirection and pipes (using >, >>, <, and |) that you don't have to worry about yet. But as long as the user doesn't try to use those features, your program should match the behavior of this reference program. This binary should run on ILE, and it will probably run on most other Linux environments you're trying to use. (I compiled it with an old-ish version of glibc.)
Environment
You should be able to complete this assignment on any *NIX operating system. For example, any of the following should work:
Linux
macOS
Your Linux VM from the first assignment
WSL2 (Windows Subsystem for Linux)
UNCG's ILE (Instructional Linux Environment) server, which you can ssh to at ile.uncg.edu. First you have to request S: drive spaceLinks to an external site. if you haven't done so already.
However, be careful with IDEs (integrated development environments) with Python. I've seen students struggle trying to use IDEs for this assignment because sometimes they don't actually fork() when your program says to, but they don't give an error either. I think it was IDLE that was doing this, but I don't remember for sure. Also you need to know how to create and submit your actual code file (.py); do not submit a notebook file. (C/C++ IDEs shouldn't have the problem with fork(), because the IDEs are actually compiling your code. But you still need to know how to put all your code into one .cpp or .c file and then submit that file.)
Testing your code
Here are four suggestions for increasing confidence that your program meets specification.

To make sure your program handles its command-line parameters and blank input lines correctly, reproduce the following sequence of runs.To understand this example sequence of runs, you need to understand three other things:
Your keyboard input is underlined, your program's output is in bold, and the output of your system shell (e.g., bash) is in normal type.
For bash's prompt, I'm just writing "bash> " here, but your bash prompt will be different.
I'm using "jsh" as the name of your shell's binary executable file, but yours may be different (just depends on what you told your compiler to name that file; it could be "a.out" by default).
I'm writing "<enter>" to indicate that I'm just pressing the enter key here. I'm not literally typing "<enter>" during the actual run.
bash> ./jsh
jsh: <enter>
jsh: echo

jsh: exit
bash> ./jsh -
<enter>
echo

exit
bash> ./jsh "testprompt: "
testprompt: <enter>
testprompt: echo

testprompt: exit
bash> ./jsh "noSpace"
noSpace<enter>
noSpaceecho

noSpaceexit
bash>
To do just some general testing that your program handles normal commands correctly, create a file named "testfile" with the following contents:
echo 1234
head -n 1 testfile
mkdir testdir
touch testdir/a
touch testdir/b
ls testdir
rm testdir/a
rm testdir/b
rmdir testdir
exit
echo Error: your program did not exit
Also, of course, make sure you don't already have a directory named "testdir" in your working directory. Now, you should be able to reproduce the following run, where the notes from the above example apply here as well:
bash> ./jsh - < testfile
1234
echo 1234
a  b
bash>      
To make sure your program handles EOF correctly, create a file named "testfile2" with just the single line "echo 1234" as its contents. Then you should be able to reproduce the following run. If you're not handling EOF correctly, you'll get an error message or your program won't exit so you won't get the system shell prompt back at the end.
bash> ./jsh - < testfile2
1234
bash>
To make sure your program correctly handles the ampersand at the end of the line (by making that process run in the background), create a file named "sleeper" with the following contents:
#!/bin/sh
sleep 10
echo Ten second sleep finished
Now, make this file an executable script by running "chmod +x sleeper" at the system command line. Once you've done that, you should be able to reproduce the following run. Note the line "" must, of course, be typed within ten seconds; if you can't type that fast, just change 10 to some higher number in the sleeper file.
bash> ./jsh
jsh: ./sleeper &
jsh: echo 1234
1234
jsh: Ten second sleep finished
echo 1234
1234
jsh: exit

bash>
Note that in the line, "jsh: Ten second sleep finished", the "jsh: " part of that appears immediately, and then the rest of the line appears after a few more seconds.
