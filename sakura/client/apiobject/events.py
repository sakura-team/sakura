def stream_events(get_remote_obj):
    try:
        while True:
            for evt_info in get_remote_obj().next_events(2.0):
                yield evt_info
    except KeyboardInterrupt:
        pass
