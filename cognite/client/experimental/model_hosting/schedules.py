from typing import Any, Dict, List, Union

from cognite.client._api_client import APIClient, CogniteCollectionResponse, CogniteResponse


class ScheduleResponse(CogniteResponse):
    def __init__(self, internal_representation):
        super().__init__(internal_representation)
        item = self.to_json()
        self.is_deprecated = item["isDeprecated"]
        self.name = item["name"]
        self.output_data_spec = item["outputDataSpec"]
        self.input_data_spec = item["inputDataSpec"]
        self.model_id = item["modelId"]
        self.created_time = item["createdTime"]
        self.metadata = item["metadata"]
        self.id = item["id"]
        self.args = item["args"]
        self.description = item["description"]
        self.last_processed_timestamp = item["lastProcessedTimestamp"]


class ScheduleCollectionResponse(CogniteCollectionResponse):
    _RESPONSE_CLASS = ScheduleResponse


class SchedulesClient(APIClient):
    def __init__(self, **kwargs):
        super().__init__(version="0.6", **kwargs)
        self._LIMIT = 1000

    def create_schedule(
        self,
        model_id: int,
        name: str,
        output_data_spec: Any,
        input_data_spec: Any,
        description: str = None,
        args: Dict = None,
        metadata: Dict = None,
    ) -> ScheduleResponse:
        """Create a new schedule on a given model.

        Args:
            model_id (int): Id of model to create schedule on
            name (str): Name of schedule
            output_data_spec (Any): Specification of output. Can be either a dictionary or a ScheduleSpec object
                                    from cognite-data-fetcher
            input_data_spec (Any): Specification of input. Can be either a dictionary or a ScheduleSpec object
                                    from cognite-data-fetcher.
            description (str): Description for schedule
            args (Dict): Dictionary of keyword arguments to pass to predict method.
            metadata (Dict): Dictionary of metadata about schedule

        Returns:
            experimental.model_hosting.schedules.ScheduleResponse: The created schedule.
        """
        url = "/analytics/models/schedules"

        if hasattr(input_data_spec, "dump"):
            input_data_spec = input_data_spec.dump()
        if hasattr(output_data_spec, "dump"):
            output_data_spec = output_data_spec.dump()

        body = {
            "name": name,
            "description": description,
            "modelId": model_id,
            "args": args or {},
            "inputDataSpec": input_data_spec,
            "outputDataSpec": output_data_spec,
            "metadata": metadata or {},
        }
        res = self._post(url, body=body)
        return ScheduleResponse(res.json())

    def list_schedules(
        self, limit: int = None, cursor: int = None, autopaging: bool = False
    ) -> ScheduleCollectionResponse:
        """Get all schedules.

        Args:
            limit (int): Maximum number of schedules to return. Defaults to 250.
            cursor (str): Cursor to use to fetch next set of results.
            autopaging (bool): Whether or not to automatically page through all results. Will disregard limit.

        Returns:
            experimental.model_hosting.schedules.ScheduleCollectionResponse: The requested schedules.
        """
        url = "/analytics/models/schedules"
        params = {"cursor": cursor, "limit": limit if autopaging is False else self._LIMIT}
        res = self._get(url, params=params)

        schedules = []
        schedules.extend(res.json()["data"]["items"])
        next_cursor = res.json()["data"].get("nextCursor")
        while next_cursor and autopaging is True:
            params["cursor"] = next_cursor
            res = self._get(url=url, params=params)
            schedules.extend(res.json()["data"]["items"])
            next_cursor = res.json()["data"].get("nextCursor")
        return ScheduleCollectionResponse({"data": {"items": schedules, "nextCursor": None}})

    def get_schedule(self, id: int) -> ScheduleResponse:
        """Get a schedule by id.

        Args:
            id (int): Id of schedule to get.
        Returns:
            experimental.model_hosting.schedules.ScheduleResponse: The requested schedule.
        """
        url = "/analytics/models/schedules/{}".format(id)
        res = self._get(url=url)
        return ScheduleResponse(res.json())

    def deprecate_schedule(self, id: int) -> ScheduleResponse:
        """Deprecate a schedule.

        Args:
            id (int): Id of schedule to deprecate

        Returns:
            experimental.model_hosting.schedules.ScheduleResponse: The deprecated schedule.
        """
        url = "/analytics/models/schedules/{}/deprecate".format(id)
        res = self._put(url)
        return ScheduleResponse(res.json())

    def delete_schedule(self, id: int) -> None:
        """Delete a schedule by id.

        Args:
            id (int):  The id of the schedule to delete.

        Returns:
            None
        """
        url = "/analytics/models/schedules/{}".format(id)
        self._delete(url=url)
