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
            print("\nUser Details (GraphQL):")
            print(f"- Name: {user.first_name} {user.last_name}")
            print(f"- Email: {user.email}")
            print(f"- ID: {user.uuid}")
            print(f"- Region: {user.region}")

            # Example: Get households using GraphQL
            households = await client.tonies.get_households()
            print("\nHouseholds (GraphQL):")
            for household in households:
                print(f"- Name: {household.name}, ID: {household.id}")

            # Example: Get Tonieboxes using GraphQL
            tonieboxes = await client.tonies.get_households_boxes()
            print("\nAll Tonieboxes (GraphQL):")
            for toniebox in tonieboxes:
                print(
                    f"- Name: {toniebox.name}, ID: {toniebox.id}, Household ID: {toniebox.household_id}"
                )

            # Example: Get Tonies overview using GraphQL
            households_with_tonies = await client.tonies.get_tonies()
            print("\nTonies Overview (GraphQL):")
            for household in households_with_tonies:
                print(f"\n--- Household: {household.name} ---")
                print("  Creative Tonies:")
                for creative_tonie in household.creative_tonies:
                    print(f"  - {creative_tonie.name} ({creative_tonie.id})")
                print("  Content Tonies:")
                for content_tonie in household.content_tonies:
                    print(f"  - {content_tonie.title} ({content_tonie.id})")

            # Example: Get children for each household
            print("\nChildren (GraphQL):")
            for household in households:
                children = await client.tonies.get_children(household.id)
                print(f"\n--- Children in Household: {household.name} ---")
                for child in children:
                    print(
                        f"- Name: {child.name}, ID: {child.id}, Gender: {child.gender}"
                    )

            # Example: Get members for each household
            print("\nMembers (GraphQL):")
            for household in households:
                members_response = await client.tonies.get_household_members(
                    household.id
                )
                print(f"\n--- Members in Household: {household.name} ---")
                for member in members_response.memberships:
                    print(
                        f"- Name: {member.display_name}, Email: {member.email}, Self: {member.is_self}"
                    )
                print("  Invitations:")
                for invitation in members_response.invitations:
                    print(f"  - Email: {invitation.email}, Type: {invitation.itype}")

            # Example: Get content tonie details
            print("\nContent Tonie Details (GraphQL):")
            if households_with_tonies and households_with_tonies[0].content_tonies:
                first_household = households_with_tonies[0]
                first_tonie = first_household.content_tonies[0]
                tonie_details_list = await client.tonies.get_content_tonie_details(
                    first_household.id, first_tonie.id
                )
                if tonie_details_list:
                    tonie_details = tonie_details_list[0]
                    print(f"Details for '{tonie_details.title}':")
                    print(f"  Description: {tonie_details.description}")
                    print(f"  Locked: {tonie_details.lock}")
                else:
                    print("Could not fetch tonie details.")

            # Example: Set max volume for a Toniebox
            print("\nSet Max Volume (REST):")
            if tonieboxes:
                first_toniebox = tonieboxes[0]
                # Test with a valid volume
                valid_volume = 75
                try:
                    print(
                        f"Setting max volume for '{first_toniebox.name}' to {valid_volume}..."
                    )
                    updated_toniebox = await client.tonies.set_max_volume(
                        first_toniebox.household_id, first_toniebox.id, valid_volume
                    )
                    print(
                        f"Success! New max volume: {updated_toniebox.max_volume}"
                    )
                except ValueError as ve:
                    print(f"Error setting volume: {ve}")

                # Test with an invalid volume
                invalid_volume = 60
                try:
                    print(
                        f"Attempting to set invalid max volume for '{first_toniebox.name}' to {invalid_volume}..."
                    )
                    await client.tonies.set_max_volume(
                        first_toniebox.household_id, first_toniebox.id, invalid_volume
                    )
                except ValueError as ve:
                    print(f"Caught expected error for invalid volume: {ve}")

                # Example: Set LED brightness for a Toniebox
                print("\nSet LED Brightness (REST):")
                # Test with a valid LED level
                valid_led_level = "dimmed"
                try:
                    print(
                        f"Setting LED level for '{first_toniebox.name}' to '{valid_led_level}'..."
                    )
                    updated_toniebox = await client.tonies.set_led_brightness(
                        first_toniebox.household_id, first_toniebox.id, valid_led_level
                    )
                    print(f"Success! New LED level: {updated_toniebox.led_level}")
                except ValueError as ve:
                    print(f"Error setting LED level: {ve}")

                # Test with an invalid LED level
                invalid_led_level = "bright"
                try:
                    print(
                        f"Attempting to set invalid LED level for '{first_toniebox.name}' to '{invalid_led_level}'..."
                    )
                    await client.tonies.set_led_brightness(
                        first_toniebox.household_id,
                        first_toniebox.id,
                        invalid_led_level,
                    )
                except ValueError as ve:
                    print(f"Caught expected error for invalid LED level: {ve}")

                # Example: Set max headphone volume for a Toniebox
                print("\nSet Max Headphone Volume (REST):")
                # Test with a valid headphone volume
                valid_headphone_volume = 75
                try:
                    print(
                        f"Setting max headphone volume for '{first_toniebox.name}' to {valid_headphone_volume}..."
                    )
                    updated_toniebox = await client.tonies.set_max_headphone_volume(
                        first_toniebox.household_id,
                        first_toniebox.id,
                        valid_headphone_volume,
                    )
                    print(
                        f"Success! New max headphone volume: {updated_toniebox.max_headphone_volume}"
                    )
                except ValueError as ve:
                    print(f"Error setting headphone volume: {ve}")

                # Test with an invalid headphone volume
                invalid_headphone_volume = 60
                try:
                    print(
                        f"Attempting to set invalid max headphone volume for '{first_toniebox.name}' to {invalid_headphone_volume}..."
                    )
                    await client.tonies.set_max_headphone_volume(
                        first_toniebox.household_id,
                        first_toniebox.id,
                        invalid_headphone_volume,
                    )
                except ValueError as ve:
                    print(f"Caught expected error for invalid headphone volume: {ve}")
            else:
                print("No Tonieboxes found to test setting max volume.")

    except TonieAuthError as e:
        print(f"Authentication failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())