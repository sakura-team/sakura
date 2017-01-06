
def get_daemon_id(sock_file):
    sock_file.write(b'GETID\n')
    sock_file.flush()
    return int(sock_file.readline().strip())
