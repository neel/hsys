class Notice:
    Error, Warning, Information = range(3)
    
    type = Information
    heading = 'Notice'
    message = 'Message'
    
    def __init__(self, type, heading, message):
        self.type = type
        self.heading = heading
        self.message = message
    