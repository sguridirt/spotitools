def chunkated(l, size):
    """Create a generator with chunks of specified length for a given list.

    Args:
        l (list): the list to be split in chunks.
        size (int): the lenght of each chunk. The last chunk may have a different size.

    Returns:
        Iterator: the generator which contains every chunk of the split list.
    """

    return (l[i : i + size] for i in range(0, len(l), size))
