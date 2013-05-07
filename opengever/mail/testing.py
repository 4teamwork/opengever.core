

class MockEvent(object):

    #History: [[interface, context], ]
    event_history = []

    def mock_handler(self, event):
        self.event_history.append(event, )

    def last_event(self):
        return self.event_history[-1]
