import hashlib

def solution(chunked_lines):
    """
    Deduplicates a stream of text chunks by filtering out consecutive groups 
    that have the exact same content, using an efficient fingerprinting key.
    """
    
    def get_hash(chunks):
        """
        Helper function to generate a composite fingerprint for a group of chunks.
        Returns:
            - A tuple of (total_bytes, binary_hash) used as a fast-lookup key.
            - The original chunks list reconstructed for output.
        """
        h = hashlib.sha256() # Initializes a blank SHA-256 hashing object.
        total_bytes = 0
        saved_chunks = []
        
        # Stream through each string fragment in the current group
        for chunk in chunks:
            # 1. Convert string to raw bytes (required for cryptographic hashing)
            data = chunk.encode('utf-8')
            
            # 2. Feed the bytes incrementally into the running SHA-256 engine
            h.update(data)
            
            # 3. Accumulate total size and store the original text fragment
            total_bytes += len(data)
            saved_chunks.append(chunk)
            
        # Optimization: Returning total_bytes first in the tuple allows Python 
        # to short-circuit inequality checks without scanning the 32-byte hash digest.
        return (total_bytes, h.digest()), saved_chunks

    # State tracking variables
    prev = None     # Stores the key tuple of the previous group
    res = []        # Stores the final deduplicated lists of chunks
    
    # Process the outer stream group-by-group
    for chunks in chunked_lines:
        # Calculate the unique cryptographic identity and retrieve saved data
        key, saved = get_hash(chunks)
        
        # If this is the first group (prev is None) OR if the identity key has changed,
        # it is not a consecutive duplicate. Append it to our results.
        if not prev or prev != key:
            res.append(saved)
            
        # Update the tracking state with the current fingerprint key for the next loop
        prev = key
        
    return res



import sys

def unique_lines(lines: list[str]):
    """
    A memory-efficient generator that filters out global duplicate lines
    from an incoming stream, yielding only unique lines in order.
    """
    # A hash set to keep track of every unique line seen so far
    # (Provides O(1) average lookup time)
    seen = set()
    
    for line in lines:
        # Strip trailing newline characters to normalize the string
        line = line.rstrip("\n")
        
        # If the line hasn't been encountered before, process it
        if line not in seen:
            seen.add(line)  # Remember this line for future checks
            yield line      # Stream the unique line out immediately without blocking

def main():
    # Ensure exactly one command-line argument (the filename) is provided
    # sys.argv[0] is the script name, sys.argv[1] is the filename
    if len(sys.argv) != 2:
        print("Usage: python unique_lines.py <filename>")
        sys.exit(1)  # Terminate the script with an error exit code

    # Extract the filename passed from the terminal
    filename = sys.argv[1]
    
    # Open the file as a readable line stream
    source = open(filename)
    
    # Use a 'with' context manager to guarantee the file handles are closed properly
    with source:
        # Pass the open file object (which acts as a stream) into our generator
        for line in unique_lines(source):
            # Write the unique lines directly to standard output (stdout)
            # Re-attaching the newline character stripped during processing
            sys.stdout.write(line + "\n")

# Standard Python boilerplate to ensure main() only runs if executed directly
if __name__ == "__main__":
    main()
