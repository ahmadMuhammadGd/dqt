from dqt.definitions import DQSuite
from pydantic import BaseModel
import pytest
from dqt.resolvers import (
    bitmap_position_to_test_bind,
    test_bind_to_bitmap_position,
    bitmap_size,
)

# pytest thinks this is a test
test_bind_to_bitmap_position.__test__ = False


class MockDQTestBind(BaseModel):
    ordinal: int
    ...


class MockDQTestSuite(BaseModel):
    test_binds: list[MockDQTestBind]


@pytest.fixture
def make_test_suite():
    def factory(ordinals):
        return MockDQTestSuite(
            test_binds=[MockDQTestBind(ordinal=ordinal) for ordinal in ordinals]
        )

    return factory


class TestTestBindBitmapCoordinates:
    @pytest.mark.parametrize(
        ("bind", "bits_per_element", "expected"),
        [
            (0, 8, (0, 0)),
            (1, 8, (0, 1)),
            (7, 8, (0, 7)),
            (8, 8, (1, 0)),
            (9, 8, (1, 1)),
            (15, 8, (1, 7)),
            (16, 8, (2, 0)),
            (31, 8, (3, 7)),
            (32, 32, (1, 0)),
            (63, 32, (1, 31)),
            (64, 32, (2, 0)),
        ],
    )
    def test_bind_to_bitmap_position(
        self,
        bind: int,
        bits_per_element: int,
        expected: tuple[int, int],
    ) -> None:
        assert (
            test_bind_to_bitmap_position(
                bind,
                bits_per_element,
            )
            == expected
        )

    @pytest.mark.parametrize(
        ("coordinates", "bits_per_element", "expected"),
        [
            ((0, 0), 8, 0),
            ((0, 1), 8, 1),
            ((0, 7), 8, 7),
            ((1, 0), 8, 8),
            ((1, 1), 8, 9),
            ((1, 7), 8, 15),
            ((2, 0), 8, 16),
            ((3, 7), 8, 31),
            ((1, 0), 32, 32),
            ((1, 31), 32, 63),
            ((2, 0), 32, 64),
        ],
    )
    def test_bitmap_position_to_test_bind(
        self,
        coordinates: tuple[int, int],
        bits_per_element: int,
        expected: int,
    ) -> None:
        assert (
            bitmap_position_to_test_bind(
                *coordinates,
                bits_per_element,
            )
            == expected
        )

    @pytest.mark.parametrize("bits_per_element", [1, 2, 8, 32, 64, 128])
    @pytest.mark.parametrize(
        "bind",
        [0, 1, 2, 7, 8, 31, 32, 63, 64, 127, 128, 1023],
    )
    def test_conversion_is_reversible(
        self,
        bind: int,
        bits_per_element: int,
    ) -> None:
        coordinates = test_bind_to_bitmap_position(
            bind,
            bits_per_element,
        )

        assert (
            bitmap_position_to_test_bind(
                *coordinates,
                bits_per_element,
            )
            == bind
        )

    @pytest.mark.parametrize(
        ("array_loc", "element_loc", "bits_per_element"),
        [
            (0, 0, 8),
            (0, 7, 8),
            (1, 0, 8),
            (10, 31, 32),
            (100, 63, 64),
        ],
    )
    def test_inverse_conversion_is_reversible(
        self,
        array_loc: int,
        element_loc: int,
        bits_per_element: int,
    ) -> None:
        bind = bitmap_position_to_test_bind(
            array_loc,
            element_loc,
            bits_per_element,
        )

        assert test_bind_to_bitmap_position(
            bind,
            bits_per_element,
        ) == (array_loc, element_loc)

    @pytest.mark.parametrize(
        ("bind", "bits_per_element"),
        [
            (-1, 8),
            (0, 0),
            (0, -1),
        ],
    )
    def test_bind_to_bitmap_position_rejects_invalid_input(
        self,
        bind: int,
        bits_per_element: int,
    ) -> None:
        with pytest.raises(ValueError):
            test_bind_to_bitmap_position(
                bind,
                bits_per_element,
            )

    @pytest.mark.parametrize(
        ("array_loc", "element_loc", "bits_per_element"),
        [
            (-1, 0, 8),
            (0, -1, 8),
            (0, 8, 8),
            (0, 0, 0),
            (0, 0, -1),
        ],
    )
    def test_bitmap_position_to_test_bind_rejects_invalid_input(
        self,
        array_loc: int,
        element_loc: int,
        bits_per_element: int,
    ) -> None:
        with pytest.raises(ValueError):
            bitmap_position_to_test_bind(
                array_loc,
                element_loc,
                bits_per_element,
            )


@pytest.mark.parametrize(
    ("ordinals", "bits_per_element", "expected"),
    [
        ([], 8, 1),
        ([0], 8, 1),
        ([1], 8, 1),
        ([7], 8, 1),
        ([8], 8, 2),
        ([9], 8, 2),
        ([15], 8, 2),
        ([16], 8, 3),
        ([0, 1, 7], 8, 1),
        ([0, 8, 15], 8, 2),
        ([1, 16, 23], 8, 3),
        ([10, 64, 127], 8, 16),
        ([0, 63], 64, 1),
        ([64], 64, 2),
        ([0, 63, 64], 64, 2),
        ([128], 64, 3),
    ],
)
def test_bitmap_size(
    ordinals,
    bits_per_element,
    expected,
    make_test_suite,
):
    suite = make_test_suite(ordinals)

    assert (
        bitmap_size(
            suite,
            bits_per_element,
        )
        == expected
    )


@pytest.mark.parametrize(
    "bits_per_element",
    [0, -1, -8],
)
def test_bitmap_size_rejects_invalid_bits_per_element(
    bits_per_element,
    make_test_suite,
):
    suite = make_test_suite([0])

    with pytest.raises(ValueError, match="bits_per_element must be positive"):
        bitmap_size(
            suite,
            bits_per_element,
        )
