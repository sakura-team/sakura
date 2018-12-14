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
        content_type = 'multipart/x-mixed-replace; boundary=frame'
        bottle.response.content_type = content_type
        # yield frames from operator on daemon
        for frame in op.stream_jpeg_frames():
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except APIObjectDeniedError as e:
        raise bottle.HTTPError(403, str(e))
    except APIRequestError as e:
        raise bottle.HTTPError(400, str(e))
