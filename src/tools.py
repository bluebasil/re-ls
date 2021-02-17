from datetime import datetime
from tabulate import tabulate
from loguru import logger
import os
import humanfriendly
import threading
import time
import sys
import reprint

# Human friendly attributes are recorded how they will be displayed to the curses_print
# Hidden attributes use snake_case
NAME = "Name"
SIZE = "Size"
RAW_SIZE = "raw_size"
LAST_MODIFIED = "Last Modified"
LAST_MODIFIED_TS = "last_modified_timestamp"
FINISHED_LOADING = "done_loading"
TYPE = "Type"
PATH = "path"
DONE = "done"
COUNT = "count"
CONTENTS = "contents"

# Map what the sort_py parameter can be, and what values in the row they refer to
sortable_features = {
    SIZE: RAW_SIZE,
    LAST_MODIFIED: LAST_MODIFIED_TS,
    NAME: NAME
}

def _determine_filetype(path):
    """
    Simple helper method

    Return FILE, DIR, or OTHER based on the filetype of the provided path
    """
    if os.path.isfile(path):
        return "FILE"
    elif os.path.isdir(path):
        return "DIR"
    else:
        return "OTHER"


class LsCompute:
    def __init__(self):
        # self.cache = {}
        self.sort_function = None
        self.desc = True
        self._clear_payload()

    def _clear_payload(self):
        self.payload = {PATH: "",
                        SIZE: "...",
                        COUNT: 0,
                        CONTENTS: [],
                        RAW_SIZE: 0}
        self.dir_store = {}
        self.thread_count = 0
        self.initialized = False
        self.payload[DONE] = False

    def _record_item(self, root_dict, path):
        """ Add the size of the record at 'path' to both the total size and the
            the size of the record in root_dict """
        # if there is an error thrown by os.stat, it's probably due to a
        # permission issue - we must simply ignore it's size
        try:
            stats = os.stat(path)
        except:
            return

        # update the row
        root_dict[RAW_SIZE] += stats.st_size
        root_dict[SIZE] = humanfriendly.format_size(root_dict[RAW_SIZE])
        # update the general/global stats
        self.payload[RAW_SIZE] += stats.st_size
        self.payload[SIZE] = humanfriendly.format_size(self.payload[RAW_SIZE])


    def _get_full_size(self, path):
        """
        Uses os.walk to sum the size of all of the files and folders under the
            given path.  Can take a long time to compute, simply due to the
            number of files, in some circumstances.
        Will set the payload into the DONE state if all the dirs have been
            initalized and this was the last thread to finish
        """

        for root, dirs, files in os.walk(path, topdown=False):
            # abord early so that we can impliemnt a q to quit
            if self.payload[DONE]:
                return

            # This really simply just records the files and folders and updates the coresponding row
            # dir_store looks up the coresponding row
            for name in files:
                self._record_item(self.dir_store[path],os.path.join(root,name))

            for name in dirs:
                self._record_item(self.dir_store[path],os.path.join(root,name))

        # Check if this was the last thread to finish
        self.thread_count -= 1
        if self.thread_count == 0 and self.initialized:
            logger.debug(f"Finished in recurse for {path}")
            logger.trace(self.payload)
            self.payload[DONE] = True

    def _sort(self):
        """ Sorts the payload contents by the sort_by param """
        def sort_function(item):
            return item[self.sort_by]
        self.payload[CONTENTS].sort(key=sort_function, reverse=self.desc)


    def _initialize_row(self, path):
        """ Sets up the inital row contents.  Not all will be visible. """
        file_stats = os.stat(path)

        # Initialize row
        return {
            NAME: os.path.basename(path),
            PATH: path,
            LAST_MODIFIED: datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %I:%M %p"),
            LAST_MODIFIED_TS: file_stats.st_mtime,
            TYPE: _determine_filetype(path),
            SIZE: "...", #Inital size and raw_size to be filled in 'record item'.
            RAW_SIZE: 0,
            FINISHED_LOADING: True # Default to true, only directories will have this as false
        }


    def ls(self, path, sort_by=SIZE, desc=True, recursive=True):
        """
        Return a Json compatable objet containing the contents of the given directly
        This json will have the inital

        Positional arguments:
        path -- The directory path of whihc you want to list all_contents

        Keyword arguments:
        sort_by -- a String, representing the desired sort by column (Default: Size)
        desc -- Boolean representing if the list should be sorted in descending order (Default: True)
        recursive -- When True, starts the process of calculating the file size of folders recursivly.
            In that case, the inital payload will still be returned, but calls to ping_output, or
            one of the print statements should be made until calculations are done. (Default: True)


        Returns a dict containing 'size' whihc represents the sum of the size of the direclty direct contents (not recursive),
            'file_count' representing the number of files that are found in the directory (Does not include ohter type: Directory, Symlink, etc.)
            and 'contents', which is a sorted list, each element being a dict with a 'name', 'size' and 'modified' field.
        """
        self._clear_payload()
        abs_path = os.path.abspath(path)

        # Have to get the full path of the files
        all_contents = [os.path.join(abs_path, f) for f in os.listdir(abs_path)]

        # Set some of the basic general/global stats
        self.payload[PATH] = abs_path
        self.payload[DONE] = False
        self.payload[COUNT] = len(all_contents)

        # Do some input validation checks
        if sort_by not in sortable_features:
            raise(ValueError(f"provided sort_by does not match any of {SIZE}, {LAST_MODIFIED}, or {NAME}."))
        self.sort_by = sortable_features[sort_by]
        self.desc = desc

        for f in all_contents:

            # initalizer the row and adds the row to the output payload
            try:
                this_row = self._initialize_row(f)
            except Exception as e:
                # os.stat can cause exceptions when there are permission or reading errors.  We will skip files of this nature
                continue
            self.payload[CONTENTS].append(this_row)

            # Adds the file's size to the payload
            self._record_item(this_row, f)

            # For directories, we must recursivly calculate their size - according to intent from Sunny
            if this_row[TYPE] == "DIR":
                this_row[FINISHED_LOADING] = False
                # dir_store is a dict to the coresponding row in the table - this is for access speed
                self.dir_store[f] = this_row

                # We will start the recursive calculations of folder contents size in another thread
                if recursive:
                    t = threading.Thread(target=self._get_full_size, args=(f,))
                    # Keeping track of how many threads we have started is a simple way of tracking if we're done
                    self.thread_count += 1
                    t.start()

        # Do an inital sort for what we will directly return
        self._sort()

        # the threads will record a done state if the thread count is zero
        # AND if this point has been reached.  otherwise the first threads can set loading to false prematurly
        # if recursive is false, we are already done
        self.initialized = True
        if self.thread_count == 0 or not recursive:
            logger.debug("Finished in ls function")
            self.payload[DONE] = True

        # Return the inital payload.  Other threads are still working
        return self.payload

    def ping_output(self):
        """
        Simply sorts the payload at it's current state of loading
        and returns the payload.  payload["done"] can be checked to see if loading is done
        """
        self._sort()
        return self.payload

    def _get_output_table(self):
        """ chooses a subset of the payload + the tabulate package to make
            and return a pretty table as a String """
        table_content = [[r[NAME],r[SIZE],r[LAST_MODIFIED]] for r in self.payload[CONTENTS]]
        table_string = tabulate(table_content, headers=[NAME, SIZE, LAST_MODIFIED])
        return table_string

    def print_output(self):
        """
        Prints the table and continues to update it, blocking while doing so
        When all recursive size calculations are finished, it will return.

        The inital table order is by inital base level calculations.
        The table will only re-order based on sort_by and desc when all other calculations are done.
        This is for processing efficiency on larger directories.

        TODO: q to quit functionality
        TODO: I am using the reprint library, which works exaclt how i want it to with smaller directories
            but larger directories thatn the size of the terminal window can be a problem.
            Additionally, preformance is a concern.  I played around with curses and manually edditing previous
            lines with limmited success.  But ideally this library should be replaces, or possibly this functionality removed entierly.
        """
        inital_table = self._get_output_table().split("\n")
        table_size = len(inital_table)
        tick = 0
        with  reprint.output(output_type='list', initial_len=table_size + 1) as output_lines:
            inital = True
            while inital or not self.payload[DONE]:
                inital = False
                split_table = self._get_output_table().split("\n")
                for i, row in enumerate(split_table):
                    output_lines[i] = row
                tail = "Loading" + "."*(tick%4)
                output_lines[table_size] = f"Count: {self.payload[COUNT]} Size: {self.payload[SIZE]} - {tail}"

                # TODO: this 'q to quit' functionality does not work
                # if keyboard.is_pressed('q'):
                #     self.payload[DONE] = True
                #     exit()

                time.sleep(0.1)
                tick += 1

            # print out the final offical version of the table
            self._sort()
            split_table = self._get_output_table().split("\n")
            for i, row in enumerate(split_table):
                output_lines[i] = row
            output_lines[table_size] = f"Count: {self.payload[COUNT]} Size: {self.payload[SIZE]} - Done."

    def quick_print_output(self):
        """
        Prints the results at it's current state of loading.
        """
        self._sort()
        print(self._get_output_table(), flush=True)
        print(f"Count: {self.payload[COUNT]} Size: {self.payload[SIZE]}", flush=True)


if __name__ == "__main__":
    # Just for testing of these tools
    logger.remove()
    logger.add(sys.stderr, level="TRACE")
    lsc = LsCompute()
    print(lsc.ls("."))
    lsc.print_output()
