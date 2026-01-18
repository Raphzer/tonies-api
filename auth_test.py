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

            # Example: Get households
            households = await client.tonies.get_households()
            print("\nHouseholds:")
            for household in households:
                print(f"- Name: {household.get('name')}, ID: {household.get('id')}")

            # Example: Get Tonies for each household
            for household in households:
                tonies = await client.tonies.get_tonies(household["id"])
                print(f"\nTonies in household '{household.get('name')}':")
                for tonie in tonies:
                    print(f"- Name: {tonie.get('name')}, Model: {tonie.get('model')}, ID: {tonie.get('id')}")


    except TonieAuthError as e:
        print(f"Authentication failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
