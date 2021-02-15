# import base64
# import paramiko
# # key = paramiko.RSAKey()
# client = paramiko.SSHClient()
# # client.get_host_keys().add('ssh.example.com', 'ssh-rsa', key)
# client.connect('ssh -R 80:localhost:8532 localhost.run')
# stdin, stdout, stderr = client.exec_command('ls')
# for line in stdout:
#     print('... ' + line.strip('\n'))
# client.close()

import subprocess
import threading
import time
import io
import re
#
# class Fo:
#     def __init__(self):
#         self.buffer = ""
#     def write(self,content):
#         print(content, flush=True)
#         self.buffer += content
#     # def __getattribute__(self,a):
#     #     print("l:",a,flush=True)
#     #     if a == "write":
#     #         return self.write
    #
    # def __getattr__(self,a):
    #     print("s:",a,flush=True)

#
# #fo = io.StringIO("BUF:")
# fo = io.BytesIO(b"some initial binary data: \x00\x01")
# #
# # fo.write(b"test")
# def fake():
#     return 1
#
# fo.fileno = fake
#
# print(subprocess.PIPE)

ssh_commend = ["ssh", "-R", "80:0.0.0.0:5000", "localhost.run", "2>&1"]
#ssh_commend = ["python", "./testouts.py", "2>&1"]
#
# proc = subprocess.Popen(["ssh", "-R", "80:0.0.0.0:5000", "localhost.run"],stderr=subprocess.PIPE, bufsize=1)
# print("?",flush=True)




def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


for path in execute(ssh_commend):
    url = re.search("^.*-.*localhost.run",path)
    if url:
        print(url[0], flush=True)
    # print(path, end="")

# try:
#     outs, errs = proc.communicate(timeout=15)
# except TimeoutExpired:
#     proc.kill()
#     outs, errs = proc.communicate()
#
# print("!",outs,errs)

# fo = Fo()
#
# def sub_process_runable():
#     fo.write("test")
#     subprocess.call(["ssh", "-R", "80:0.0.0.0:5000", "localhost.run"],stderr=subprocess.PIPE, bufsize=1)
#
#
# t = threading.Thread(target=sub_process_runable)
# # t.start()
# while True:
#     print("Content:")
#     print(fo.readlines(), flush=True)
#     fo.seek(0)
#     # print(fo.buffer, flush=True)
#     time.sleep(1)
