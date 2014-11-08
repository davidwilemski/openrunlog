
import StringIO

from react import jsx
from tornado import web


class JSXStaticFileHandler(web.StaticFileHandler):
    @classmethod
    def get_content(cls, abspath, start=None, end=None):
        # Only override in the case of a JSX file
        ext = abspath.split('.')[-1]
        if ext.lower() != 'jsx':
            static = super(JSXStaticFileHandler, cls).get_content(
                abspath, start=start, end=end)

            for x in static:
                yield x
            return

        content = jsx.transform(abspath)
        buf = StringIO.StringIO(content)

        if start is not None:
            buf.seek(start)

        if end is not None:
            remaining = end - (start or 0)
        else:
            remaining = None

        chunk_size = 64 * 1024
        while True:
            if remaining is not None and remaining < chunk_size:
                chunk_size = remaining

            chunk = buf.read(chunk_size)

            if chunk:
                if remaining is not None:
                    remaining -= len(chunk)
                yield chunk

            else:
                if remaining is not None:
                    assert remaining == 0
                return

    def get_content_type(self):
        ext = self.absolute_path.split('.')[-1]
        if ext.lower() == 'jsx':
            return 'text/javascript'

        return super(JSXStaticFileHandler, self).get_content_type()
