import sys

def stream_filter():
    """
    Streams text from standard input, removes numbers, 
    converts text to uppercase, and writes to standard output.
    """
    try:
        # Loop over lines from standard input as a real-time data stream
        for line in sys.stdin:
            # 1. Transform: Convert line to uppercase
            upper_line = line.upper()
            
            # 2. Filter: Remove any numbers/digits from the text
            clean_line = "".join([char for char in upper_line if not char.isdigit()])
            
            # 3. Output: Write directly to standard output stream
            sys.stdout.write(clean_line)
            
            # 4. Flush: Force Python to empty the memory buffer immediately
            sys.stdout.flush()
            
    except KeyboardInterrupt:
        # Gracefully exit if the user presses Ctrl+C
        sys.exit(0)

if __name__ == "__main__":
    stream_filter()
