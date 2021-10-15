"""
Tutaj się nie postarałem, troche bałagan, 
kod może być niezrozumiały ale niestety mało czasu
"""

import json

import pandas as pd
import requests
from blood_tests.services import blood_test_passed_create, blood_test_rejected_create
from django.conf import settings

api_key = settings.API_KEY


class BloodTestHandler:
    def __init__(self, blood_test_file) -> None:
        self.blood_test_file = blood_test_file

    def get_dataframe(self, file) -> pd.DataFrame:
        """

        Generate and return dataframe from csv file

        Args:
            file_path (str): full file path

        Returns:
            pd.DataFrame: dataframe object
        """
        file_path = file
        df = pd.read_csv(
            file_path,
            sep=";",
        )
        print(df)
        return df

    def df_convert(self, file) -> dict:
        """
        Creates a dict with patient id as key and list of results as value

        Args:
            data (pd.DataFrame): Data

        Returns:
            dict:
        """
        data = self.get_dataframe(file)

        user_tests_dict = {}
        for row_dict in data.to_dict(orient="records"):

            current_user = row_dict.pop("id")

            if not current_user in user_tests_dict.keys():
                user_tests_dict[current_user] = [
                    row_dict,
                ]
            else:
                user_tests_dict[current_user].append(row_dict)
        return user_tests_dict

    def handle_request(self, file):
        for patient_id, results_list in self.df_convert(file).items():

            url = "https://bloodlab-demo.appspot.com/v1/diagnosis/"
            headers = {
                "X-API-KEY": api_key,
                "Content-Type": "application/json",
            }

            request_dict = {
                "id_system": str(patient_id),
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
            json_data = json.dumps(request_dict, indent=2)

            r = requests.post(url=url, data=json_data, headers=headers)

            if r.status_code == 201:
                res_content = json.loads(r.content)

                blood_test_passed_create(
                    request_sent=json_data,
                    response_http_code=r.status_code,
                    response_time=r.elapsed.total_seconds(),
                    feedback=res_content["feedback"],
                )

            else:
                blood_test_rejected_create(
                    error_code=r.status_code,
                    response_time=r.elapsed.total_seconds(),
                    request_sent=json_data,
                    response_data=str(r.content),
                )
            print(r.elapsed.total_seconds())
            print(r.status_code)
