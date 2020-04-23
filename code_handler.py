import glob
import os
import subprocess

allowed_commands = ['ls','run','opn','put']

def parse(command):
    if command.split()[0] not in allowed_commands:
        return 'Error occured'
    commandt = command.split()[0]
    arguments = list()
    for i in command.split(' '):
        if i != commandt:
            arguments.append(i)
        else:
            pass
    if commandt == 'ls':
        if len(arguments)>=2 and arguments[1] == 'npth' :
             return os.listdir(arguments[0])
        elif len(arguments)!= 0:
            files = os.listdir(arguments[0])
            pthfiles = list()
            for i in files:
                pthfiles.append(arguments[0]+i)
            return pthfiles
        else:
            return 'No path or arguments given.'
    elif commandt == 'run':
        if len(arguments) == 1:
            try:
                subprocess.call(arguments[0], shell=False)
                return 'Done.'
            except Exception:
                return 'Error occured'
        else:
            return 'Error occured'
    elif commandt == 'opn':
        if len(arguments) == 1:
            f = open(arguments[0],'r')
            data = f.read()
            f.close()
            return(data)
        else:
            return 'Error occured'
    elif commandt == 'put':
        if len(arguments) == 2:
            f = open(arguments[0],'w')
            f.write(arguments[1])
            f.close()
            return('Done.')
        else:
            return 'Error occured'
