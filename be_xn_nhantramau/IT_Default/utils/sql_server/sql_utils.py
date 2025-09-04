# Tạo bộ lọc nâng cao và phân tích
def sql_build_advanced_filters_and_pagination(request, exclude_filter=None):
    if exclude_filter is None:
        exclude_filter = []

    filters = {}
    pagination = {
        "page": 1,
        "limit": 10,
        "ordering": None
    }
    params = {}

    for param_key, value in request.query_params.items():
        params[param_key] = value

        # Skip parameters that are in the exclude list
        if param_key in exclude_filter:
            continue

        if value in ["", None]:
            continue

        # Extract pagination and ordering
        if param_key == "page":
            try:
                pagination["page"] = int(value)
            except ValueError:
                pass
            continue

        if param_key == "limit":
            try:
                pagination["limit"] = int(value)
            except ValueError:
                pass
            continue

        if param_key == "ordering":
            pagination["ordering"] = value
            continue

        filters[param_key] = value

    return filters, pagination, params
