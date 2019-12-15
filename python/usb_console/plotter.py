import pylab as plt
import matplotlib.dates as mdates
from .gpstime import GPSTime
from tinydb import TinyDB, Query
from argparse import ArgumentParser
import cmd, sys

class StateFieldPlotter(object):
    """
    Plotting utility for processing data, both live during the simulation and in
    post-processing.
    """

    def __init__(self, db = None):
        self.db = db

        # Clear plot and set plotting ticker parameters
        date_locator = mdates.AutoDateLocator()
        plt.gca().xaxis.set_major_formatter(
            mdates.AutoDateFormatter(date_locator))
        plt.gca().xaxis.set_major_locator(date_locator)

    def find_timeseries(self, field, db = None):
        if not db:
            db = self.db
        if not db:
            print("Database is not available for searching.")
            return None

        field_data = []
        query = db.search(Query().field == field)
        for row in query:
            field_data.append((row["time"], row["val"]))

        if len(field_data) == 0:
            print(
                f"Could not find any data for field with name \"{field}\"."
            )
            return None
        else:
            return field_data

    def add_timeseries(self, field, field_data):
        """
        Add time series for a state field named "field" to the plot.
        Expects an array of time-value pairs. The times should be datetime strings.
        """

        # Process times in data
        data_t = [mdates.datestr2num(datapoint[0]) for datapoint in field_data]

        # Process values in data
        if field_data[0][1].count(",") == 2:
            # It's a GPS time
            data_vals = [
                GPSTime(datapoint[1]).to_ns() for datapoint in field_data
            ]
            plt.plot(data_t, data_vals, label=field)
        elif field_data[0][1].count(",") == 3:
            # It's a vector
            data_vals = [datapoint[1].split(",") for datapoint in field_data]
            data_vals_x = [float(dataval[0]) for dataval in data_vals]
            data_vals_y = [float(dataval[1]) for dataval in data_vals]
            data_vals_z = [float(dataval[2]) for dataval in data_vals]
            plt.plot(data_t, data_vals_x, label=field + ".x")
            plt.plot(data_t, data_vals_y, label=field + ".y")
            plt.plot(data_t, data_vals_z, label=field + ".z")
        elif field_data[0][1].count(",") == 4:
            # It's a quaternion
            data_vals = [datapoint[1].split(",") for datapoint in field_data]
            data_vals_w = [float(dataval[0]) for dataval in data_vals]
            data_vals_x = [float(dataval[1]) for dataval in data_vals]
            data_vals_y = [float(dataval[2]) for dataval in data_vals]
            data_vals_z = [float(dataval[3]) for dataval in data_vals]
            plt.plot(data_t, data_vals_w, label=field + ".w")
            plt.plot(data_t, data_vals_x, label=field + ".x")
            plt.plot(data_t, data_vals_y, label=field + ".y")
            plt.plot(data_t, data_vals_z, label=field + ".z")
        else:
            if field_data[0][1] in ["true", "false"]:
                # It's a boolean
                data_vals = [(1 if datapoint == "true" else 0)
                             for datapoint in field_data]
            else:
                try:
                    # It might be an integer
                    data_vals = [int(datapoint[1]) for datapoint in field_data]
                except ValueError:
                    try:
                        # It's a float or double
                        data_vals = [
                            float(datapoint[1]) for datapoint in field_data
                        ]
                    except ValueError:
                        print(f"Field {field} is not of a plottable type.")
                        return

            plt.plot(data_t, data_vals, label=field)

        return True

    def display(self):
        plt.gcf().autofmt_xdate()
        plt.legend()
        plt.show()
        plt.clf()

class PlotterClient(cmd.Cmd):
    def __init__(self, db):
        self.db = db
        self.plotter = StateFieldPlotter(self.db)

        self.intro = "Type \"plot x\" to plot state field \"x\".\n"
        self.prompt = "> "
        super().__init__()

    def do_plot(self, args):
        args = args.split()
        print(args)
        if len(args) == 0:
            print("Need to specify at least one state field to plot.")
            return

        for field in args:
            field_data = self.plotter.find_timeseries(field, self.db)
            if not field_data:
                return
            self.plotter.add_timeseries(field, field_data)

        self.plotter.display()

    def do_exit(self, args):
        sys.exit()

    def do_quit(self, args):
        sys.exit()

if __name__ == "__main__":
    if sys.version_info[0] != 3 or sys.version_info[1] < 6:
        print("Running this script requires Python 3.6 or above.")
        sys.exit(1)

    parser = ArgumentParser("""Allows plotting data after a simulation has ended.""")
    parser.add_argument(
        '-d',
        '--data',
        action='store',
        help=
        '''Location of data telemetry file, relative to the current working directory.''',
        required=True)

    args = parser.parse_args()

    db = TinyDB(args.data)
    plotter = PlotterClient(db)

    try:
        plotter.cmdloop()
    except KeyboardInterrupt:
        # Gracefully exit session
        plotter.do_quit(None)
        print("Exiting due to keyboard interrupt.")
        sys.exit()
