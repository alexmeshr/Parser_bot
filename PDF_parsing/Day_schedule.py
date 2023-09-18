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
        for col in data:
            self.schedule[col] = data[col]

    def get_table_for_group(self, group):
        return self.schedule[group]