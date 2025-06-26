import pytest
import csv
from main import (
    get_data,
    parse_filter_condition,
    parse_aggregate_condition,
    filter_data,
    aggregate_data,
    print_data,
    get_args
)


@pytest.fixture
def sample_data():
    return [
        {"name": "iphone 15 pro", "brand": "apple", "price": "999",
         "rating": "4.9"},
        {"name": "galaxy s23 ultra", "brand": "samsung", "price": "1199",
         "rating": "4.8"},
        {"name": "redmi note 12", "brand": "xiaomi", "price": "199",
         "rating": "4.6"},
    ]


def test_get_data(tmp_path):
    csv_content = """name,brand,price,rating
iphone 15 pro,apple,999,4.9
galaxy s23 ultra,samsung,1199,4.8"""

    file_path = tmp_path / "test.csv"
    file_path.write_text(csv_content)

    data = get_data(file_path)
    assert len(data) == 2
    assert data[0]["name"] == "iphone 15 pro"
    assert data[1]["brand"] == "samsung"


def test_parse_filter_condition():
    assert parse_filter_condition("price>1000") == ("price", ">", "1000")
    assert parse_filter_condition("brand=apple") == ("brand", "=", "apple")
    assert parse_filter_condition("rating>=4.5") == ("rating", ">=", "4.5")

    with pytest.raises(ValueError):
        parse_filter_condition("price>")
    with pytest.raises(ValueError):
        parse_filter_condition(">1000")
    with pytest.raises(ValueError):
        parse_filter_condition("price!1000")


def test_parse_aggregate_condition():
    assert parse_aggregate_condition("price=avg") == ("price", "avg")
    assert parse_aggregate_condition("rating=max") == ("rating", "max")
    assert parse_aggregate_condition("price=min") == ("price", "min")

    with pytest.raises(ValueError):
        parse_aggregate_condition("price=")
    with pytest.raises(ValueError):
        parse_aggregate_condition("price=sum")
    with pytest.raises(ValueError):
        parse_aggregate_condition("=avg")


def test_filter_data(sample_data):
    filtered = filter_data(sample_data, "price>500")
    assert len(filtered) == 2
    assert filtered[0]["name"] == "iphone 15 pro"
    assert filtered[1]["name"] == "galaxy s23 ultra"

    filtered = filter_data(sample_data, "brand=apple")
    assert len(filtered) == 1
    assert filtered[0]["name"] == "iphone 15 pro"

    with pytest.raises(KeyError):
        filter_data(sample_data, "nonexistent>100")

    with pytest.raises(ValueError):
        filter_data(sample_data, "brand>100")
    with pytest.raises(ValueError):
        filter_data(sample_data, "price>apple")


def test_aggregate_data(sample_data):
    aggregated = aggregate_data(sample_data, "price=avg")
    assert len(aggregated) == 1
    assert aggregated[0]["avg"] == pytest.approx((999 + 1199 + 199) / 3)

    aggregated = aggregate_data(sample_data, "price=max")
    assert aggregated[0]["max"] == 1199

    aggregated = aggregate_data(sample_data, "price=min")
    assert aggregated[0]["min"] == 199

    with pytest.raises(KeyError):
        aggregate_data(sample_data, "nonexistent=avg")

    with pytest.raises(ValueError):
        aggregate_data(sample_data, "name=avg")


def test_print_data(sample_data, capsys):
    print_data(sample_data)
    captured = capsys.readouterr()
    assert "iphone 15 pro" in captured.out
    assert "apple" in captured.out
    assert "samsung" in captured.out

    print_data([])
    captured = capsys.readouterr()
    assert "No rows matching the conditions were found" in captured.out


def test_get_args(monkeypatch):
    test_args = ["--file", "test.csv", "--where", "price>100", "--aggregate",
                 "price=avg"]
    monkeypatch.setattr("sys.argv", ["main.py"] + test_args)
    args = get_args()

    assert args.file == "test.csv"
    assert args.where == "price>100"
    assert args.aggregate == "price=avg"


def test_main_integration(monkeypatch, capsys):
    test_args = ["main.py", "--file", "products.csv", "--where", "brand=apple",
                 "--aggregate", "price=avg"]
    monkeypatch.setattr("sys.argv", test_args)

    import main
    main.main()

    captured = capsys.readouterr()
    assert "avg" in captured.out
    assert "706.5" in captured.out