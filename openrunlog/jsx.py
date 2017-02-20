
import StringIO

from react import jsx
from tornado import web


class JSXStaticFileHandler(web.StaticFileHandler):
    @classmethod
    def get_content(cls, abspath, start=None, end=None):
        # Only override in the case of a JSX file
        if not cls._is_jsx_file(abspath):
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

    @staticmethod
    def _is_jsx_file(path):
        ext = path.split('.')[-1]
        return ext.lower() == 'jsx'

    def get_content_type(self):
        if self._is_jsx_file(self.absolute_path):
            return 'text/javascript'

        return super(JSXStaticFileHandler, self).get_content_type()

    def get_content_size(self):
        if self._is_jsx_file(self.absolute_path):
            return len(jsx.transform(self.absolute_path))
        return super(JSXStaticFileHandler, self).get_content_size()
