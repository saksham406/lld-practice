import string


class Base62Encoder:

    BASE = 62
    CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits
    def encode(self, num, total_lenght=6):
        if num == 0:
            return self.CHARS[0]
        result = []
        while num > 0:

            remainder = num % self.BASE

            result.append(self.CHARS[remainder])

            num //= self.BASE

        code =  ''.join(reversed(result))
        return code.zfill(total_lenght)
    

class UrlShortner:
    def __init__(self):
        self.id_counter = 1
        self.url_map = {}
        self.encoder = Base62Encoder()

    def short_url(self, url):
        code = self.encoder.encode(self.id_counter)
        self.url_map[code] = url
        self.id_counter += 1
        return code

    def redirect(self, code):
        return self.url_map.get(code)

shortner = UrlShortner()
url = 'https://www.google.com'
short_code = shortner.short_url(url)
print(short_code)
print(shortner.redirect(short_code))