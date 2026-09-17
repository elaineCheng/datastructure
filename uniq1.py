import hashlib
import tempfile
import os
import heapq
import sys


def get_partition(line, num_partitions):
    """
    Deterministically routes a line to a specific partition index using MD5 hashing.
    Guarantees that identical text strings will always land in the exact same partition file.
    """
        
    h = hashlib.md5(line.encode()).hexdigest()
    return int(h, 16) % num_partitions

def partition_file(file_name, num_partitions):
    """
    PHASE 1: Distributes lines from a massive file into smaller, manageable partition files.
    Prefixes each line with its original file position line number to preserve order.
    """
    # Create an array of open, unnamed scratch files on disk
    files = [
        tempfile.NamedTemporaryFile(
            mode="w",
            delete=False
        ) 
        for _ in range(num_partitions)
    ]
    try:
        with open(file_name, "r") as f:
            # Stream the input file line-by-line along with its original line index (position)
            for position, line in enumerate(f):
                partition = get_partition(line, num_partitions)
                # Save the structural metadata (position) attached to the data payload
                files[partition].write(
                    f"{position}\t{line}"
                )

    finally:
        # Explicitly flush buffers and close file descriptors to safe disk states
        for file in files:
            file.close()
    # Return a list of raw string file paths to find the data in the next step
    return [f.name for f in files]

def dedupe_partition(file_name):
    """
    PHASE 2A: Performs an in-memory unique constraint evaluation on a single partition file.
    """
    seen = {} # Maps unique line string text -> its first discovered absolute line position
    with open(file_name, "r") as f:
        for record in f:
            # Separate the prefixed index back out from the data line
            position, line = record.split("\t", 1)
            position = int(position)
            # Global unique isolation: only record the absolute first occurrence of this string
            if line not in seen:
                seen[line] = position

    # Unpack the key-value structure into an array of positional tuples
    return [
        (position, line) for line, position in seen.items()
    ]

def write_sorted_partition(records):
    """
    Sort deduplicated records by original position
    and write them to a temporary file.
    """

    # Sort strictly by the original line number sequence (x[0]) to fix layout scrambled by hashing
    records.sort(key=lambda x: x[0])
    file = tempfile.NamedTemporaryFile(
        mode="w",
        delete=False
    )

    try:
        for position, line in records:
            file.write(f"{position}\t{line}")
    finally:
        file.close()

    return file.name # Return sorted intermediate file path for k-way streaming

def read_records(file):
    """
        Streaming Helper: Dynamically streams structured records back out of disk buffers.
        Read reords from a sorted partition.
        Yields:
            (position, line)
    """

    for record in file:
        position, line = record.split("\t", 1)
        yield int(position), line

def merge_partitions(sorted_files):
    """
    PHASE 3: Executes a K-Way Merge over all partition streams simultaneously.
    Pulls records sequentially, processing them in correct chronological order via a Min-Heap.
    """

    files = [
        open(file_name, "r")
        for file_name in sorted_files
    ]

    try:
        iterators = [
            read_records(file)
            for file in files
        ]

        # heapq.merge streams lines concurrently from all pointers,
        # yielding whichever line possesses the lowest original 'position' index next.

        for position, line in heapq.merge(
            *iterators,
            key=lambda x:x[0]
        ):
            sys.stdout.write(line)

    finally:
        for file in files:
            file.close()

class UniqueLineProcessor:
    """
    Orchestration Engine: Manages life cycles, execution pathways, and file cleanup for the pipeline.
    """
    def __init__(self, num_partitions=10):
        self.num_partitions = num_partitions

    def process(self, file_name):
        partition_files = []
        sorted_partition_files = []

        try:
            # phase 1: parition
                partition_files = partition_file(file_name, self.num_partitions)


            #phase 2: local deduplication

                for partition in partition_files:
                    records = dedupe_partition(partition)
                    sorted_file = write_sorted_partition(records)
                    sorted_partition_files.append(sorted_file)

            # phase 3: merge
                merge_partitions(sorted_partition_files)

        finally:
            for file_name in partition_files:
                if os.path.exists(file_name):
                    os.remove(file_name)
            for file_name in sorted_partition_files:
                if os.path.exists(file_name):
                    os.remove(file_name)

def main():
    if len(sys.argv) != 2:
        print("Usage: python unq_1.py <file>")
        return
    processor = UniqueLineProcessor(
        num_partitions=10
    )
    processor.process(sys.argv[1])

if __name__ == "__main__":
    main()
