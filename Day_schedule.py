from datetime import date


class Day_schedule:
    groups = []
    date = None
    schedule = {}

    def __init__(self, date, groups):
        self.date = date
        self.groups = groups
        self.schedule = {g:{} for g in groups}


    def import_data(self, data):
        pass
