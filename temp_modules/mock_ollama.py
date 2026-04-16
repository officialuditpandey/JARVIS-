
class MockListResponse:
    def __init__(self):
        self.models = [{'name': 'llama3.1:8b'}]
    
    def __len__(self):
        return len(self.models)

def list():
    return MockListResponse()
