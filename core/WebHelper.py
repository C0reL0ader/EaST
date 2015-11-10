import cookielib
import urllib2
import urllib

class FormPoster:
    def __init__(self):
        self.BOUNDARY = '----------ThIs_Is_tHe_saLteD_bouNdaRY_$'
        self.fields = []
        self.files = []

    def post(self, target, additional_headers={}):
        """
        Post fields and files to an http target as multipart/form-data.
        additional_headers can add new headers or overwrite existing.
        Return the server's response page.
        """
        request = urllib2.Request(target)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0')
        content_type, body = self._encode_multipart_formdata()
        request.add_header('Content-Type', content_type)
        request.add_header('Content-Length', str(len(body)))
        if type(additional_headers) is dict:
            for key in additional_headers:
                request.add_header(key, additional_headers[key])
        request.add_data(body)
        return urllib2.urlopen(request).read()

    def _encode_multipart_formdata(self):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body)
        """
        CRLF = '\r\n'
        L = []
        for (key, value) in self.fields:
            L.append('--' + self.BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value, content_type) in self.files:
            L.append('--' + self.BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            if content_type:
                L.append('Content-Type: %s' % content_type)
            L.append('')
            L.append(value)
        L.append('--' + self.BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % self.BOUNDARY
        return content_type, body

    def add_field(self, key, value):
        self.fields.append((key, value))

    def add_file(self, key, filename, file, is_path=True, content_type=''):
        """Add file entry to a form.
        If 'is_path' - True 'file' must be path to file
        If 'is_path' - False 'file' - is text content
        """
        file = open(file, 'rb').read() if is_path else file
        self.files.append((key, filename, file, content_type))

class NoRedirection(urllib2.HTTPErrorProcessor):
    """ Creates no redirection handler
    For example:
    no_redir = NoRedirection()
    print no_redir.open_http_address("http://habr.ru").geturl()
    """

    def http_response(self, request, response):
        return response

    def open_http_address(self, address):
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cj))
        response = opener.open(address)
        return response

    https_response = http_response

