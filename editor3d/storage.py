import pickle


class Storage:
    def __init__(self, filename, root_object):
        self.filename = filename
        self.root = root_object
        try:
            with open(self.filename, 'rb') as file:
                self.root = pickle.load(file)
        except FileNotFoundError:
            pass
        except EOFError:
            print("Database corrupted.")

    def get_root(self):
        return self.root

    def schedule_store(self):
        # Todo: Scheduler to wait for 5s for further changes before storing
        self.store()

    def store(self):
        with open(self.filename, 'wb') as file:
            pickle.dump(self.root, file)
