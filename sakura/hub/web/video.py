import bottle
from sakura.common.errors import APIRequestError, APIObjectDeniedError

def serve_video_stream(context, op_id):
    try:
        # TODO: check rights on operator
        op = context.op_instances.get(id=op_id)
        if op is None:
            raise bottle.HTTPError(404, 'Invalid operator identifier.')
        print('serving video stream...')
        # let browser know our content type (i.e. motion jpeg format)
        content_type = 'multipart/x-mixed-replace; boundary=boundary'
        bottle.response.content_type = content_type
        # yield frames from operator on daemon.
        # note: due to a bug in chrome and firefox
        # (https://bugs.chromium.org/p/chromium/issues/detail?id=527446)
        # a frame is not displayed before the header of the next one is
        # received. That's why we first yield the multipart boundary and
        # the content-type before waiting for the frame to be generated.
        iterator = enumerate(op.stream_jpeg_frames())
        while True:
            yield (b'--boundary\r\n' +
               b'Content-Type: image/jpeg\r\n\r\n')
            i, frame = next(iterator)
            print(i)
            yield (frame + b'\r\n')
    except APIObjectDeniedError as e:
        raise bottle.HTTPError(403, str(e))
    except APIRequestError as e:
        raise bottle.HTTPError(400, str(e))
    print('stream ended')
