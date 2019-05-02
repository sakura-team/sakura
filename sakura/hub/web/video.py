import bottle
from sakura.common.errors import APIRequestError, APIObjectDeniedError

def serve_video_stream(context, op_id, ogl_id, width, height):
    try:
        # TODO: check rights on operator
        op = context.op_instances.get(id=op_id)
        if op is None:
            raise bottle.HTTPError(404, 'Invalid operator identifier.')
        if ogl_id < 0 or ogl_id >= len(op.opengl_apps):
            raise bottle.HTTPError(404, 'Invalid opengl app ID.')
        opengl_app = op.opengl_apps[ogl_id]
        print('serving video stream... %dx%d' % (width, height))
        # let browser know our content type (i.e. motion jpeg format)
        content_type = 'multipart/x-mixed-replace; boundary=boundary'
        bottle.response.content_type = content_type
        # yield frames from operator on daemon.
        # note: due to a bug in chrome and firefox
        # (https://bugs.chromium.org/p/chromium/issues/detail?id=527446)
        # a frame is not displayed before the header of the next one is
        # received. That's why we first yield the multipart boundary and
        # the content-type before waiting for the frame to be generated.
        iterator = enumerate(opengl_app.stream_jpeg_frames(width, height))
        while True:
            yield (b'--boundary\r\n' +
               b'Content-Type: image/jpeg\r\n\r\n')
            i, frame = next(iterator)
            print(i, len(frame))
            # send 1024-bytes chunks
            for j in range((len(frame)-1)//1024 + 1):
                yield frame[j*1024:(j+1)*1024]
            yield b'\r\n'
    except APIObjectDeniedError as e:
        raise bottle.HTTPError(403, str(e))
    except GeneratorExit:
        # the browser closed the connection.
        print('stream ended (browser disconnection)')
        # in case this is unexpected, notify javascript code so that it
        # reopens a new stream.
        opengl_app.push_event('browser_disconnect', width, height)
    except StopIteration:
        # when the video size changes on browser, a new stream with
        # different width & height is opened.
        # the old stream detects it is now obsolete, stops and we
        # get here.
        print('stream ended (on daemon)')
    except BaseException as e:
        raise bottle.HTTPError(400, str(e))
