import os, pwd

pw = pwd.getpwnam("nobody")
orig_uid = pw.pw_uid
orig_gid = pw.pw_gid

print os.getuid(), os.getgid(), os.geteuid(), os.getegid(), orig_uid, orig_gid

os.setgid(orig_gid)
os.setuid(orig_uid)
