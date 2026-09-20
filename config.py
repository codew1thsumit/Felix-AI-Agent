import sys
import io
#removing the AFC message error in Terminal
class FilterAFC(io.TextIOBase):
    def __init__(self, original):
        self.original = original

    def write(self, text):
        if "Direct use of automatic function calling (AFC)" not in text:
            return self.original.write(text)
        return len(text)

    def flush(self):
        self.original.flush()


sys.stderr = FilterAFC(sys.stderr)