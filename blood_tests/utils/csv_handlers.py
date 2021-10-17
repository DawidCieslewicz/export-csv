"""
Tutaj się nie postarałem, troche bałagan, 
kod może być niezrozumiały ale niestety mało czasu
"""

import json

import pandas as pd
import requests
from blood_tests.services import (blood_test_passed_create,
                                  blood_test_rejected_create)
from django.conf import settings
from requests.models import Response

api_key = settings.API_KEY


class BloodTestHandler:
    def __init__(self, blood_test_file) -> None:
        self.blood_test_file = blood_test_file

        if not str(blood_test_file).endswith('.csv'):
            raise NotImplementedError("Cannot read files other than .csv")

    def get_dataframe(self, file) -> pd.DataFrame:
        """

        Generate dataframe from csv file

        Returns:
            pd.DataFrame: dataframe object
        """

        df: pd.DataFrame = pd.read_csv(
            file,
            sep=";",
        )

        df_column_names = df.columns.values.tolist()
        df_required_columns = ['id', 'parameter', 'unit',
                               'value_numeric', 'marker', 'low', 'high']

        if not set(df_required_columns) == set(df_column_names):
            raise NotImplementedError(
                "Column names does not match required pattern"
            )

        return df

    def df_convert(self) -> dict:
        """
        Creates a dict with patient id as key and list of results as value

        Args:
            data (pd.DataFrame): Data

        Returns:
            dict: {"patient_id": [results,]}
        """
        data = self.get_dataframe(self.blood_test_file)

        user_tests_dict = {}
        for row_dict in data.to_dict(orient="records"):

            current_user = str(row_dict.pop("id"))

            if not current_user in user_tests_dict.keys():
                user_tests_dict[current_user] = [
                    row_dict,
                ]
            else:
                user_tests_dict[current_user].append(row_dict)
        return user_tests_dict

    def generate_json_data(self, patient_id, results_list):
        """
            Create json object that fits api
        """
        request_dict = {
            "id_system": patient_id,
            "sex": "f",
            "date_of_birth": "1989-01-01",
            "lab_tests": [
                {
                    "name": "morfologia",
                    "package_code": "PK001",
                    "test_date": "2021-07-01",
                    "lab_test_results": results_list,
                }
            ],
        }
        json_data = json.dumps(request_dict)

        return json_data

    def handle_request(self, request, response: Response):
        if response.status_code == 201:
            response_content_json = json.loads(response.content)

            blood_test_passed_create(
                request_sent=request,
                response_http_code=response.status_code,
                response_time=response.elapsed.total_seconds(),
                feedback=response_content_json["feedback"],
            )

        else:
            blood_test_rejected_create(
                error_code=response.status_code,
                response_time=response.elapsed.total_seconds(),
                request_sent=request,
                response_data=response.content,
            )

    def send_blood_test_request(self):
        """
            Send request and deal with results
        """
        url = "https://bloodlab-demo.appspot.com/v1/diagnosis/"

        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        }

        for patient_id, results_list in self.df_convert().items():

            json_data = self.generate_json_data(
                patient_id=patient_id,
                results_list=results_list
            )

            r = requests.post(url=url, data=json_data, headers=headers)

            self.handle_request(request=json_data, response=r)
