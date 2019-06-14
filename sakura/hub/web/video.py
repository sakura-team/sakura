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
        # let browser know our content type
        content_type = 'video/mp4'
        bottle.response.content_type = content_type
        bottle.response.headers['Access-Control-Allow-Origin'] = '*'
        # yield frames from operator on daemon.
        streamer = opengl_app.get_streamer(width, height)
        yield from streamer.stream_video()
        # when the video size changes on browser, a new stream with
        # different width & height is opened.
        # the old stream detects it is now obsolete, stops and we
        # get here.
        print('stream ended (on daemon)')
        streamer.stop()
    except APIObjectDeniedError as e:
        raise bottle.HTTPError(403, str(e))
    except GeneratorExit:
        streamer.stop()
        # the browser closed the connection.
        print('stream ended (browser disconnection)')
        # in case this is unexpected, notify javascript code so that it
        # reopens a new stream.
        opengl_app.push_event('browser_disconnect', width, height)
    except BaseException as e:
        #import pdb; pdb.set_trace()
        raise bottle.HTTPError(400, str(e))
