import progressbar

class PBar:
    def __init__(self, label, maxValue=100, minValue = 0, width=120):
        widgets = [label.ljust(22), ' ', progressbar.Percentage(), ' ', progressbar.Bar(), ' ',
            progressbar.Timer(), ' ', progressbar.ETA(format_finished='              ')]

        self.minValue = minValue
        self.maxValue = maxValue
        self.bar = progressbar.ProgressBar(widgets=widgets, maxval=maxValue, term_width=width).start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f"An exception of type {exc_type} occurred.")
        return False

    def do_something(self):
        print("Doing something within the context")

    def update(self, value):
        clamped = min(max(value, self.minValue), self.maxValue)
        self.bar.update(clamped)

    def getTime(self):
        return (self.bar.last_update_time - self.bar.start_time).total_seconds()

    def finish(self):
        self.bar.finish()
