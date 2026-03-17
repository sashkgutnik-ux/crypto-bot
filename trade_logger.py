import csv

class CSVLoader:

    def __init__(self, file_path):
        self.file_path = file_path

    def load_prices(self):

        prices = []

        with open(self.file_path, "r") as file:

            reader = csv.reader(file)

            for row in reader:

                close_price = float(row[4])
                prices.append(close_price)

        return prices