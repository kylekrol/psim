import readline
from cmd import Cmd
import random
import timeit

class StateCmdPrompt(Cmd):
    '''
    This command prompt is used by the user to read and write to write to the state of
    Teensies and simulation devices.
    '''

    def __init__(self, devices, exit_fn):
        self.devices = devices
        self.exit_fn = exit_fn

        if not self.devices:
            # There's no flight controller to connect with.
            raise SystemExit

        # By default, if it's available, set the prompt to be commanding the Flight Controller.
        try:
            self.cmded_device = self.devices['FlightController']
        except KeyError:
            self.cmded_device = random.choice(list(self.devices.values()))

        Cmd.__init__(self)

    def emptyline(self):
        # Don't do anything with an empty line input
        pass

    def do_cc(self, args):
        '''
        Lists the Teensy currently being interacted with by the user.
        '''
        print(f"Currently interacting with {self.cmded_device.device_name}")

    def do_lc(self, args):
        '''
        Lists all available Teensies.
        '''
        print("Available devices:")
        for device_name in self.devices.keys():
            print(device_name)

    def do_sc(self, args):
        '''
        Switches the Teensy that the user is controlling by the command line.
        '''
        args = args.split()

        if len(args) < 1:
            print('Need to specify a device to command')
            return

        try:
            self.cmded_device = self.devices[args[0]]
        except KeyError:
            print('Invalid device specified')
            return

        print(f"Switched to {self.cmded_device.device_name}")

    def do_rs(self, args):
        '''
        Read state. See state_session.py for documentation.
        '''
        args = args.split()

        if len(args) < 1:
            print('Need to specify a state field to read')
            return

        start_time = timeit.default_timer()
        read_result = self.cmded_device.read_state(args[0])
        elapsed_time = int((timeit.default_timer() - start_time) * 1E6)
        print(f"{read_result} \t\t\t\t\t\t(Completed in {elapsed_time} us)")

    def do_ws(self, args):
        '''
        Write state. See state_session.py for documentation.
        '''
        args = args.split()

        if len(args) < 1:
            print('Need to specify a state field to set')
            return
        elif len(args) < 2:
            print('Need to specify the value to set')
            return

        start_time = timeit.default_timer()
        write_succeeded = self.cmded_device.write_state(args[0], args[1])
        elapsed_time = int((timeit.default_timer() - start_time) * 1E6)

        write_succeeded = "Succeeded" if write_succeeded else "Failed"
        print(f"{write_succeeded} \t\t\t\t\t\t(Completed in {elapsed_time} us)")

    def do_os(self, args):
        '''
        Override simulation state. See state_session.py for documentation.
        '''
        args = args.split()
        start_time = timeit.default_timer()
        override_succeeded = self.cmded_device.override_state(args[0], args[1])
        elapsed_time = int((timeit.default_timer() - start_time) * 1E6)

        override_succeeded = "Succeeded" if override_succeeded else "Failed"
        print(f"{override_succeeded} \t\t\t\t\t\t(Completed in {elapsed_time} us)")

    def do_ro(self, args):
        '''
        Release override of simulation state. See state_session.py for documentation.
        '''
        args = args.split()
        self.cmded_device.release_override(args[0])

    def do_quit(self, args):
        '''
        Exits the command line and terminates connections with the flight computer(s).
        '''
        self.exit_fn('Exiting command line.')

    def do_exit(self, args):
        '''
        Exits the command line and terminates connections with the flight computer(s).
        '''
        self.do_quit(None)
