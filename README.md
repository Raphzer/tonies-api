# Tonies API Client

A Python library for interacting with the Tonies API. This library provides an asynchronous client to manage your Tonies, Creative-Tonies, households, and more.

## Features

-   Asynchronous client based on `httpx`.
-   OAuth2 authentication flow for the Tonies API.
-   GraphQL support for fetching data.
-   Pydantic models for data validation and type hinting.
-   Fetches:
    -   User details
    -   Households
    -   Tonieboxes
    -   Creative-Tonies and Content-Tonies
    -   Children in a household
    -   Household members

## Installation

You can install the library directly from the source:

```bash
git clone https://github.com/your-username/tonies-api.git
cd tonies-api
pip install -r requirements.txt
```

## Usage

First, create a `.env` file in your project root with your Tonies credentials:

```
TONIE_USERNAME=your_email@example.com
TONIE_PASSWORD=your_password
```

Then, you can use the `TonieAPIClient` to interact with the API. Here is a basic example:

```python
import asyncio
import os

from dotenv import load_dotenv

from tonies_api.client import TonieAPIClient
from tonies_api.exceptions import TonieAuthError


async def main():
    """Run a test of the Tonies API."""
    load_dotenv()

    username = os.getenv("TONIE_USERNAME")
    password = os.getenv("TONIE_PASSWORD")

    if not username or not password:
        print("Please set TONIE_USERNAME and TONIE_PASSWORD in your .env file.")
        return

    try:
        async with TonieAPIClient(username, password) as client:
            print("Login successful!")

            # Example: Get user details using GraphQL
            user = await client.tonies.get_user_details()
            print(f"Welcome, {user.first_name}!")

            # Example: Get households using GraphQL
            households = await client.tonies.get_households()
            for household in households:
                print(f"Household: {household.name}")

            # Example: Get Tonieboxes using GraphQL
            tonieboxes = await client.tonies.get_households_boxes()
            if tonieboxes:
                first_toniebox = tonieboxes[0]
                
                # Example: Set max volume for a Toniebox
                try:
                    updated_toniebox = await client.tonies.set_max_volume(
                        first_toniebox.household_id, first_toniebox.id, 75
                    )
                    print(f"Success! New max volume: {updated_toniebox.max_volume}")
                except ValueError as ve:
                    print(f"Error setting volume: {ve}")

                # Example: Set Toniebox name
                try:
                    updated_toniebox = await client.tonies.set_toniebox_name(
                        first_toniebox.household_id, first_toniebox.id, "My Test Toniebox"
                    )
                    print(f"Success! New Toniebox name: {updated_toniebox.name}")
                except ValueError as ve:
                    print(f"Error setting Toniebox name: {ve}")

    except TonieAuthError as e:
        print(f"Authentication failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())

```

## API Reference

The `TonieAPIClient` provides access to the `TonieResources` class via the `tonies` attribute. Here are some of the available methods:

-   `get_user_details() -> User`
-   `get_households() -> List[Household]`
-   `get_households_boxes() -> List[Toniebox]`
-   `get_tonies() -> List[HouseholdWithTonies]`
-   `get_children(household_id: str) -> List[Child]`
-   `get_household_members(household_id: str) -> HouseholdMembersResponse`
-   `get_content_tonie_details(household_id: str, tonie_id: str) -> List[ContentTonieDetails]`
-   `set_max_volume(household_id: str, toniebox_id: str, max_volume: int) -> Toniebox`
-   `set_led_brightness(household_id: str, toniebox_id: str, led_level: str) -> Toniebox`
-   `set_max_headphone_volume(household_id: str, toniebox_id: str, max_headphone_volume: int) -> Toniebox`
-   `set_toniebox_name(household_id: str, toniebox_id: str, name: str) -> Toniebox`
-   `set_accelerometer(household_id: str, toniebox_id: str, enabled: bool) -> Toniebox`
-   `set_tap_direction(household_id: str, toniebox_id: str, direction: str) -> Toniebox`
-   `set_lightring_brightness(household_id: str, toniebox_id: str, brightness: int) -> Toniebox`
-   `set_bedtime_max_volume(household_id: str, toniebox_id: str, volume: int) -> Toniebox`
-   `set_bedtime_headphone_volume(household_id: str, toniebox_id: str, volume: int) -> Toniebox`
-   `set_bedtime_lightring_brightness(household_id: str, toniebox_id: str, brightness: int) -> Toniebox`

All methods are asynchronous and should be awaited.


## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
