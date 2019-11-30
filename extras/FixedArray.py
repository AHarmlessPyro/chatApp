class FixedArray:

    def __init__(self, max_size=10):
        self.MAX_SIZE = max_size
        self.currentSize = 0
        self.lst = []

    def __len__(self):
        return self.currentSize

    def __getitem__(self, key: int):
        if(key < self.MAX_SIZE):
            return self.lst[key]
        raise IndexError

    def __setitem__(self, key: int, value):
        if(key < self.MAX_SIZE):
            for i in range(self.MAX_SIZE - 1, key-1, -1):
                self.lst[i] = self.lst[i-1]
            self.lst[key] = value
        raise IndexError

    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        iter(self.lst)

    def __reversed__(self):
        raise NotImplementedError

    def __contains__(self, item):
        for entry in self.lst:
            if item == entry:
                return True
        return False
