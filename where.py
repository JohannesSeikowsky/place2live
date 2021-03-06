"""The script for analysis of the characteristics of different countries."""
import difflib
from typing import Dict

import pandas as pd

from utils import text_color, text_type


class Index:
    """[summary]"""

    __slots__ = ("name", "text", "value", "mood")

    def __init__(self, name=None, text=None, mood=None):
        self.name = name or ""
        self.text = text if text else " ".join(self.name.split("_"))
        self.mood = mood


class Place2Live:
    """[summary]

    Returns:
        [type] -- [description]
    """

    countries_df = None

    default_values = {
        "purchasing_power_index": 200,
        "safety_index": 200,
        "health_care_index": 200,
        "cost_of_living_index": 0,
        "property_price_to_income_ratio": 0,
        "traffic_commute_time_index": 0,
        "pollution_index": 0,
        "climate_index": 200,
    }

    desired_indexes: Dict[str, float] = {}

    indexes_for_dialog = (
        Index(name="purchasing_power_index", mood="higher is better"),
        Index(name="safety_index", mood="higher is better"),
        Index(name="health_care_index", mood="higher is better"),
        Index(name="climate_index", mood="higher is better"),
        Index(name="cost_of_living_index", mood="lower is better"),
        Index(name="property_price_to_income_ratio", mood="lower is better"),
        Index(name="traffic_commute_time_index", mood="lower is better"),
        Index(name="pollution_index", mood="lower is better"),
    )

    def __init__(self, source_data_path=None):
        """[summary]

        Keyword Arguments:     source_data_path {[type]} --
        [description] (default: {None})
        """
        if source_data_path:
            # TODO: add file check and error handling
            self.countries_df = pd.read_csv(source_data_path)
            self.countries_df.fillna(value=self.default_values)

            self.user_country_name = self.ask_user_country()
            self.user_country = self.countries_df[
                self.countries_df.country == self.user_country_name
            ]

    def start_dialog(self):
        """[summary]"""
        for index in self.indexes_for_dialog:
            index.value = float(self.user_country[index.name])
            self.print_user_country_info(index)
            self.desired_indexes[index.name] = self.ask_desired_index(index)

    def get_closest_country(self, country_name: str):
        """This function finds the closest match for the country."""
        countries = self.countries_df["country"].values.tolist()
        closest_match = difflib.get_close_matches(country_name, countries)
        return str(closest_match).strip("[]").replace(",", " or")

    def ask_user_country(self):
        """Checks for a valid country by checking df."""
        while True:
            country_name = input(
                text_color("What is your country? ", text_type.QUESTION),
            )
            country_name = country_name.title()
            try:
                float(
                    self.countries_df[self.countries_df.country == country_name][
                        "purchasing_power_index"
                    ],
                )
            except TypeError:
                closest_country = self.get_closest_country(country_name)
                error_str = f"{country_name} is an invalid country or did you mean {closest_country}. Please try again."

                if not closest_country:
                    error_str = (
                        f"{country_name} is an invalid country name. Please try again."
                    )

                print(text_color(error_str, text_type.WARNING))

            else:
                return country_name

    def print_user_country_info(self, index):
        """[summary]

        Arguments:
            index {[type]} -- [description]
        """
        print(self.format_info(index.text, index.value))

    def ask_desired_index(self, index):
        """[summary]

        Arguments:
            index {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        question = self.format_question(
            index.text, self.max_min_index(index.name), index.mood,
        )
        default = index.value
        while True:
            index_input = input(question)

            if self.is_float(index_input):
                return float(index_input)
            elif not index_input:
                return default

            print(
                text_color(
                    f"'{index_input}' is an invalid index. Please try again.",
                    text_type.WARNING,
                ),
            )

    def max_min_index(self, index_name):
        """Return maximum and minimum value with country of a column from
        df."""
        country_and_name = self.countries_df[["country", index_name]]
        counrties_in_name_index = country_and_name.sort_values(index_name).dropna()
        min_value = [
            list(counrties_in_name_index[index_name])[0],
            list(counrties_in_name_index["country"])[0],
        ]
        max_value = [
            list(counrties_in_name_index[index_name])[-1],
            list(counrties_in_name_index["country"])[-1],
        ]
        return max_value, min_value

    @staticmethod
    def format_info(column_title, value):
        """[summary]

        Arguments:
            column_title {[type]} -- [description]
            value {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        return text_color(
            f"In your country {column_title} is {value}", text_type.ANSWER,
        )

    @staticmethod
    def format_question(name_index, max_min_value, mood):
        """Return a question that asks the user about the status of a factor in
        his country.

        Also displays the maximum and minimum value of this factor in
        the world.
        """

        if mood == "lower is better":
            max_min_value = max_min_value[::-1]

        best_value, best_value_country_name = max_min_value[0]
        worst_value, worst_value_country_name = max_min_value[1]
        message = text_color(
            f"What is your desirable {name_index} ({mood})? "
            f"The best score in the world is "
            f"{best_value} "
            f"({best_value_country_name}), "
            f"the worst is {worst_value} "
            f"({worst_value_country_name}) ",
            text_type.QUESTION,
        )
        return message

    @staticmethod
    def is_float(index_input):
        """Helper function to validate float values."""
        try:
            float(index_input)
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    PLACE2LIVE = Place2Live(
        source_data_path="create_db/scraper/scraped_data/countries.csv",
    )
    PLACE2LIVE.start_dialog()
    DF = PLACE2LIVE.countries_df
    desired: Dict[str, float] = PLACE2LIVE.desired_indexes

    OUT_DF = DF[
        (DF.purchasing_power_index > desired["purchasing_power_index"])
        & (DF.safety_index > desired["safety_index"])
        & (DF.health_care_index > desired["health_care_index"])
        & (DF.cost_of_living_index < desired["cost_of_living_index"])
        & (
            DF.property_price_to_income_ratio
            < desired["property_price_to_income_ratio"]
        )
        & (DF.traffic_commute_time_index < desired["traffic_commute_time_index"])
        & (DF.pollution_index < desired["pollution_index"])
        & (DF.climate_index > desired["climate_index"])
    ]

    PRINT_OUT_DF = (
        OUT_DF[["country", "freedomhouse_score", "quality_of_life_index"]]
        .dropna()
        .sort_values(by=["freedomhouse_score"], ascending=False)
    )

    if PRINT_OUT_DF.empty:
        print(
            text_color(
                "There is no country better than {}.".format(
                    PLACE2LIVE.user_country_name
                ),
                text_type.ANSWER,
            ),
        )
    else:
        with pd.option_context("display.max_rows", None, "display.max_columns", None):
            print(text_color(PRINT_OUT_DF.to_string(index=False), text_type.ANSWER))
