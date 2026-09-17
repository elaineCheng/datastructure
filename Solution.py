def part1(lines):
    res = []
    for line in lines:
        if not res or res[-1] != line:
            res.append(line)
    return res


            
def part2(lines):
    if isinstance(lines, str):
        iterator = iter((lines,))
    else:
        iterator = iter(lines)

    result = []
    previous = None

    for line in iterator:
        if line != previous:
            result.append(line)
            previous = line

    return result


def solution(chunked_lines):
    import hashlib

    def get_hash(chunks):
        h = hashlib.sha256()
        total_bytes = 0
        saved_chunks = []

        for chunk in chunks:
            data = chunk.encode('utf-8')
            h.update(data)
            total_bytes += len(data)
            saved_chunks.append(chunk)
        return (total_bytes, h.digest()), saved_chunks

    
    prev = None
    res = []

    for chunks in chunked_lines:
        key, saved = get_hash(chunks)
        if not prev or prev != key:
            res.append(saved)
            prev = key
    
    return res


def part4(lines):
    prev = None
    cnt = 0
    res = []
    if not lines:
        return res
    for line in lines:
        if prev and prev != line:
            res.append([cnt, prev])
            prev = line
            cnt = 1
        else:
            prev = line
            cnt += 1
    res.append([cnt, prev])
    return res

def main():
    input_1 = ['apple\n', 'apple\n', 'banana\n', 'banana\n', 'apple\n']
    input_2 = [['app', 'le'], ['apple'], ['ban', 'ana'], ['ban', 'ana'], ['app', 'le']]
    input_3 = []
    input_4 = ['apple', 'apple', 'banana', 'apple', 'apple', 'carrot', 'carrot']

    print(part4(input_3))
    print(part4(input_4))

if __name__ == "__main__":
    main()
