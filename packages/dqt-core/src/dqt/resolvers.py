from dqt.definitions import DQSuite


def test_bind_to_bitmap_position(
    bind: int,
    bits_per_element: int,
) -> tuple[int, int]:
    """Resolve a test bind into its bitmap element coordinates.

    A test bind is a zero-based bit position in the logical DQ violation
    bitmap. The bitmap is represented as elements containing a fixed number
    of bits, so this function maps the linear bind position to the element
    containing it and the bit position within that element.

    Args:
        bind: Zero-based linear test bind position.
        bits_per_element: Number of bits available in each bitmap element.

    Returns:
        A tuple of ``(array_loc, element_loc)`` where ``array_loc`` is the
        zero-based bitmap element index and ``element_loc`` is the
        zero-based bit position within that element.

    Raises:
        ValueError: If ``bits_per_element`` is not positive.
        ValueError: If ``bind`` is negative.
    """
    if bind < 0:
        raise ValueError("bind must be non-negative")
    if bits_per_element <= 0:
        raise ValueError("bits_per_element must be positive")

    array_loc = bind // bits_per_element
    element_loc = bind % bits_per_element

    return array_loc, element_loc


def bitmap_position_to_test_bind(
    array_loc: int,
    element_loc: int,
    bits_per_element: int,
) -> int:
    """Resolve bitmap element coordinates into a linear test bind.

    This is the inverse operation of :func:`resolve_test_bind_to_x_y`.
    Coordinates are zero-based: ``array_loc`` identifies the bitmap element,
    while ``element_loc`` identifies the bit position within that element.

    Args:
        array_loc: Zero-based bitmap element index.
        element_loc: Zero-based bit position within the bitmap element.
        bits_per_element: Number of bits available in each bitmap element.

    Returns:
        The zero-based linear test bind represented by the coordinates.

    Raises:
        ValueError: If ``bits_per_element`` is not positive.
        ValueError: If either coordinate is negative.
        ValueError: If ``element_loc`` is outside the bitmap element.
    """
    if array_loc < 0:
        raise ValueError("array_loc must be non-negative")
    if element_loc < 0:
        raise ValueError("element_loc must be non-negative")
    if bits_per_element <= 0:
        raise ValueError("bits_per_element must be positive")
    if element_loc >= bits_per_element:
        raise ValueError("element_loc must be less than bits_per_element")

    return array_loc * bits_per_element + element_loc


def bitmap_size(suite: DQSuite, bites_per_element: int) -> int:
    """
    Return the number of elements required to store a suite's test bitmap.
    Test binds are represented as zero-based positions in a logical bitmap.
    Each bitmap element stores ``bits_per_element`` bits.
    The required bitmap size is therefore determined by the highest test-bind ordinal in the suite.
    An empty suite requires one bitmap element so that the bitmap maintains a stable, non-empty representation.

    Args:
        suite: DQ test suite whose test binds determine the bitmap size.
        bits_per_element: Number of bits available in each bitmap element.

    Returns:
        The number of bitmap elements required to represent all test binds.

    Raises:
        ValueError: If ``bits_per_element`` is not positive.
    """
    if not suite.test_binds:
        return 1

    max_ordinal = max(test_bind.ordinal for test_bind in suite.test_binds)

    array_loc, _ = test_bind_to_bitmap_position(
        max_ordinal,
        bites_per_element,
    )

    return array_loc + 1
