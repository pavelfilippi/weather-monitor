import pytest


@pytest.mark.asyncio
async def test_query_zero_stations():
    """ Query returns empty result for empty db """
    query = """
        query TestQuery {
            meteostations {
                battery_percentage
                location
            }
        }
    """

    result = await schema.execute(query)

    assert result.data["meteostations"] == []
