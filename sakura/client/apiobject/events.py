def stream_events(api):
    try:
        while True:
            for evt_info in api.events.next_events(2.0):
                yield evt_info
    except KeyboardInterrupt:
        pass
